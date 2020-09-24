import copy
from typing import List, Dict, Set, Tuple, Optional

from solver.Solver import Solver


# Dynamic Largest Individual Sum split.
class DLIS(Solver):
    # noinspection DuplicatedCode
    def _split(
            self,
            clauses: List[Set[int]],
            solution: Dict[int, bool],
            order: List[bool],
            backtrace: Set[int] = None,
            stack: List[int] = None
    ) -> Tuple[bool, Dict[int, bool], List[Set[int]], Optional[int]]:
        if backtrace is None:
            backtrace = set()
        if stack is None:
            stack = []

        # Get all variables from the clauses.
        unresolved: Dict[int, int] = {}
        for clause in clauses:
            for literal in clause:
                variable = abs(literal)

                if solution[variable] is not None or literal in backtrace or literal * -1 in backtrace:
                    continue
                if literal not in unresolved:
                    unresolved[literal] = 0
                if literal * -1 not in unresolved:
                    # This should never happen, because it indicates the existence of a pure literal.
                    unresolved[literal * -1] = 0
                unresolved[literal] += 1

            # We will resolve the open variables in order of total frequency (both negative and positive literals
            # combined).
            sort: List[Tuple[int, int]] = [*sorted(unresolved.items(), key=lambda x: x[1], reverse=True)]

            for direction in order:
                for literal, frq in sort:
                    variable: int = abs(literal)
                    polarity: bool = direction if unresolved[literal] > unresolved[literal * -1] else not direction
                    # Append the current literal to the backtrace, so that it won't get scanned again.
                    backtrace.add(literal)
                    # Re-run the algorithm with a new literal value.
                    success, _solution, _clauses, conflict = self._dp(
                        # Do a deep copy, because otherwise it gets stuck with clause simplifications from previous
                        # attempts.
                        copy.deepcopy(clauses),
                        {**solution, variable: polarity},
                        {literal},
                        backtrace={*backtrace},
                        stack=[*stack, literal],
                        order=order
                    )
                    if success:
                        return success, _solution, _clauses, conflict

            return False, solution, clauses, None
