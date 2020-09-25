import collections
import time
import traceback

from mxklabs.dimacs import Dimacs
from abc import ABC, abstractmethod
from typing import Set, Dict, List, Tuple, Optional

DP_LIMIT = 2500
PURE_LITERALS = False


class Solver(ABC):
    def __init__(
            self,
            problem: Dimacs,
            pure_literals: bool = PURE_LITERALS
    ):
        # Optimisation flag.
        self.pure_literals: bool = pure_literals

        # Initialisation of class properties.
        self.clauses: List[Set[int]] = [*map(lambda _clause: {*_clause}, problem.clauses)]
        self.solution: Dict[int, Optional[bool]] = dict.fromkeys(
            sorted({abs(literal) for clause in self.clauses for literal in clause}),
            None
        )

        # Benchmark variables.
        self.start: float = 0
        self.end: float = 0
        self.dp_calls: int = 0
        self.split_calls: int = 0
        self.solution_attempts: int = 0
        self.known: Set[int] = {[*clause][0] for clause in self.clauses if len(clause) == 1}
        self.frequencies = collections.Counter([literal % 10 for literal in self.known]).most_common()

    def solve(self, **extra_vars):
        self.start = time.process_time()

        try:
            success, solution, clauses, conflict = self._dp(self.clauses, self.solution, **extra_vars)
        except Exception as e:
            self.end = time.process_time()
            print(e)
            # print(traceback.format_exc())
            return False, None, None, None

        self.end = time.process_time()
        return success, solution, clauses, conflict

    def _dp(
            self,
            clauses: List[Set[int]],
            solution: Dict[int, Optional[bool]],
            **extra_vars
    ) -> Tuple[bool, Optional[Dict[int, bool]], List[Set[int]], Optional[int]]:
        self.dp_calls += 1
        if self.dp_calls > DP_LIMIT:
            self.end = time.process_time()
            raise Exception("Unsolvable, limit of {} DP calls exceeded.".format(DP_LIMIT))

        while True:
            # Copy the clauses, because otherwise the loop will break if we remove items from the iteration.
            for clause in [*clauses]:
                success, conflicting_variable = self._simplify_clause(clause, clauses, solution)
                if success is False:
                    return False, solution, clauses, conflicting_variable
                elif success is True:
                    # Break the loop, because something changed
                    break

            # Nothing changed, because the loop was not broken or returned. Therefore stop running DP.
            else:
                break

        # Test if there are still unresolved clauses, which means that we're not done yet with parsing.
        if len(clauses) != 0:
            self.split_calls += 1
            # Perform a Split operation.
            return self._split(clauses, solution, **extra_vars)

        # Found a solution!
        return True, solution, clauses, None

    def _simplify_clause(
            self,
            clause: Set[int],                     # The clause to simplify
            clauses: List[Set[int]],              # Required if we intend to purge the clause
            solution: Dict[int, Optional[bool]],  # The current solution
    ) -> (bool, int):
        """"
        The first return value is False if we encountered a contradiction and should stop processing this solution.
        The second return value provides the variable that caused a conflict.
        """
        length: int = len(clause)

        # Test for empty clauses.
        if length == 0:
            # An empty clause means that we have a contradiction.
            return False, None

        # Test for unit clauses.
        if length == 1:
            literal = [*clause][0]
            success = self._resolve(literal, clauses, solution)
            return success, None if success else abs(literal)

        # Remove all tautologies (clauses that will always resolve to True).
        if length != len(Solver.extract_clause_vars(clause)):
            clauses.remove(clause)
            return True, None

        # Nothing has changed.
        return None, None

    def _resolve(self, literal: int, clauses: List[Set[int]], solution: Dict[int, Optional[bool]]) -> bool:
        """Adds a literal to the current solution, if possible."""
        variable: int = abs(literal)
        polar_literal: int = literal * -1
        polarity: bool = variable == literal

        # Only write to resolved and unprocessed when necessary.
        if solution[variable] is None:
            solution[variable]: bool = polarity

            for _clause in [*clauses]:
                if literal in _clause:
                    # The literal will resolve to True and thus the whole clause will be True.
                    clauses.remove(_clause)
                elif polar_literal in _clause:
                    if len(_clause) == 1:
                        # We encountered a contradiction, because we cannot expect unit clauses with the polar
                        # literal value, since we already added the literal to the solution.
                        return False
                    # The polar literal will resolve to False and thus can be purged from all clauses.
                    _clause.remove(polar_literal)

        # We encountered a contradiction, because the current solution already contains a different value for this
        # variable.
        elif solution[variable] != polarity:
            return False

        if polarity:
            self.solution_attempts += 1

        # The current solution is still solvable.
        return True

    @staticmethod
    def extract_clause_vars(clause: Set[int]) -> Set[int]:
        """Get the variable name from all literals in the clause by removing any hyphens."""
        return {*map(lambda literal: abs(literal), clause)}

    @abstractmethod
    def _split(
            self,
            clauses: List[Set[int]],
            solution: Dict[int, bool],
            **extra_vars
    ) -> Tuple[bool, Dict[int, bool], List[Set[int]], Optional[int]]:
        pass
