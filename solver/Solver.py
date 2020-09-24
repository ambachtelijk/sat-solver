import collections
import time

from mxklabs.dimacs import Dimacs
from abc import ABC, abstractmethod
from typing import Set, Dict, List, Tuple, Optional

DP_LIMIT = 1000000


class Solver(ABC):
    def __init__(
            self,
            problem: Dimacs,
            preprocess: bool = True,
            pure_literals: bool = False
    ):
        # Optimisation flags.
        self.preprocess: bool = preprocess
        self.pure_literals: bool = pure_literals

        # Initialisation of class properties.
        self.clauses: List[Set[int]] = [*map(lambda _clause: {*_clause}, problem.clauses)]
        self.solution: Dict[int, Optional[bool]] = dict.fromkeys(
            sorted({abs(literal) for clause in self.clauses for literal in clause}),
            None
        )
        self.unprocessed: Set[int] = set()

        # Benchmark variables.
        self.start: float = 0
        self.end: float = 0
        self.dp_calls: int = 0
        self.literal_searches: int = 0
        self.literal_iterations: int = 0
        self.known: Set[int] = {[*clause][0] for clause in self.clauses if len(clause) == 1}
        self.frequencies = collections.Counter([literal % 10 for literal in self.known]).most_common()

    def solve(self, **extra_vars):
        self.start = time.process_time()

        # Simply prepend the solvable clauses to problem clauses, because the Davis-Putman algorithm will solve the
        # clauses early on anyway, so there is no need to run the algorithm twice.
        if self.preprocess:
            for clause in [*self.clauses]:
                removed, success, conflict = self.simplify_clauses(
                    clause,
                    self.clauses,
                    self.solution,
                    self.unprocessed
                )
                if success is False:
                    return False, self.solution, self.clauses, conflict

        success, solution, clauses, conflict = self._dp(self.clauses, self.solution, self.unprocessed, **extra_vars)

        self.end = time.process_time()

        return success, solution, clauses, conflict

    def _dp(
            self,
            clauses: List[Set[int]],
            solution: Dict[int, Optional[bool]],
            unprocessed: Set[int],
            **extra_vars
    ) -> Tuple[bool, Dict[int, bool], List[Set[int]], Optional[int]]:
        self.dp_calls += 1
        if self.dp_calls > DP_LIMIT:
            raise Exception("Unsolvable, limit of {} DP calls exceeded.".format(DP_LIMIT))

        # Test for pure literals.
        pure_literals: Dict[int, int] = {}
        rejected_variables: Set[int] = set()
        new_unprocessed: Set[int] = set()

        # Copy the clauses, because otherwise the loop will break if we remove items from the iteration.
        for clause in [*clauses]:
            removed: bool = False
            # Remove all clauses that contain a resolved variable.
            for literal in unprocessed:
                self.literal_iterations += 1
                self.literal_searches += 1
                # Remove the whole clause if it contains the resolved literal (therefore the clause resolves to True).
                if literal in clause:
                    clauses.remove(clause)
                    removed = True
                    break

                # Remove the opposite literal from the clause, because the instance will resolve to False.
                polar_literal: int = literal * -1
                self.literal_searches += 1
                if polar_literal in clause:
                    clause.remove(polar_literal)
                    clauses[clauses.index(clause)] = clause
                    # Test for empty clauses.
                    if len(clause) == 0:
                        return False, solution, clauses, abs(literal)

                    # Test for unit clauses.
                    if len(clause) == 1:
                        clauses.remove(clause)
                        removed = True
                        unit_literal = [*clause][0]
                        # Since there is only one literal left in this clause, we can resolve it to True (called unit
                        # propagation).
                        if not self.resolve(unit_literal, solution, new_unprocessed):
                            # We encountered a contradiction.
                            return False, solution, clauses, abs(unit_literal)
            if removed:
                continue

            # We are only going to simplify the clauses if this hasn't been done in a preprocess pass before.
            if not self.preprocess:
                removed, success, conflict = self.simplify_clauses(clause, clauses, solution, unprocessed)
                if success is False:
                    return False, solution, clauses, conflict
                if removed:
                    continue

            if self.pure_literals:
                # Keep track of all pure literals that we may encounter.
                for literal in clause:
                    self.literal_iterations += 1
                    variable: int = abs(literal)

                    # Keep track if this literal was marked as not pure, so we don't have to probe it again.
                    self.literal_searches += 1
                    if variable in rejected_variables:
                        continue
                    polar_literal: int = literal * -1

                    # The current literal is not pure, because its opposite value exists.
                    self.literal_searches += 1
                    if polar_literal in pure_literals:
                        pure_literals.pop(polar_literal)
                        rejected_variables.add(variable)
                    else:
                        pure_literals[variable]: int = literal

        if self.pure_literals:
            # Test for pure literals.
            self.literal_searches += 1
            for variable in pure_literals:
                if not self.resolve(pure_literals[variable], solution, new_unprocessed):
                    # We encountered a contradiction.
                    return False, solution, clauses, abs(pure_literals[variable])

        # There is still something to process, rerun with the current context.
        if len(new_unprocessed) != 0:
            return self._dp(clauses, solution, new_unprocessed, **extra_vars)

        # Test if there are still unresolved clauses, which means that we're not done yet with parsing.
        elif len(clauses) != 0:
            # Perform a Split operation.
            return self._split(clauses, solution, **extra_vars)

        # Found a solution!
        return True, solution, clauses, None

    def resolve(self, literal: int, resolved: Dict[int, Optional[bool]], unprocessed: Set[int]) -> bool:
        variable: int = abs(literal)
        polarity: bool = variable == literal

        # Only write to resolved and unprocessed when necessary.
        if resolved[variable] is None:
            resolved[variable]: bool = polarity
            unprocessed.add(literal)

        # We encountered a contradiction.
        elif resolved[variable] != polarity:
            return False

        return True

    def extract_clause_vars(self, clause: Set[int]) -> Set[int]:
        def cb(literal):
            self.literal_iterations += 1
            return abs(literal)

        # Get the variable name from all literals in the clause by removing any hyphens.
        return {*map(cb, clause)}

    def remove_literal(self, clause: Set[int], literal: int) -> Set[int]:
        self.literal_searches += 1
        if literal in clause:
            clause.remove(literal)
        return clause

    def simplify_clauses(
            self,
            clause: Set[int],
            clauses: List[Set[int]],
            solution: Dict[int, Optional[bool]],
            unprocessed: Set[int]
    ) -> (bool, bool, int):
        # Test for empty clauses.
        if len(clause) == 0:
            return True, False, None

        # Remove all tautologies.
        if len(clause) != len(self.extract_clause_vars(clause)):
            clauses.remove(clause)
            return True, True, None

        # Test for unit clauses.
        if len(clause) == 1:
            clauses.remove(clause)
            literal = [*clause][0]
            # Since there is only one literal left in this clause, we can resolve it to True (called unit
            # propagation).
            return True, self.resolve(literal, solution, unprocessed), abs(literal)

        return False, True, None

    @abstractmethod
    def _split(
            self,
            clauses: List[Set[int]],
            solution: Dict[int, bool],
            order: List[bool],
            backtrace: Set[int] = None,
            stack: List[int] = None
    ) -> Tuple[bool, Dict[int, bool], List[Set[int]], Optional[int]]:
        pass
