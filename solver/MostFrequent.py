import copy
from typing import List, Dict, Set, Tuple, Optional

from solver.Solver import Solver


class MostFrequent(Solver):
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

        # We will resolve the open variables in order of total frequency (both negative and positive literals combined).
        for direction in order:
            for variable, polarity in solution.items():
                if polarity is not None or variable in backtrace or variable * -1 in backtrace:
                    continue

                literal: int = variable if direction else variable * -1
                # Append the current literal to the backtrace, so that it won't get scanned again.
                backtrace.add(literal)

                # Re-run the algorithm with a new literal value.
                success, _resolved, _clauses, conflict = self._dp(
                    # Do a deep copy, because otherwise it gets stuck with clause simplifications from previous attempts
                    copy.deepcopy(clauses),
                    {**solution, variable: direction},
                    {literal},
                    backtrace={*backtrace},
                    stack=[*stack, literal],
                    order=order
                )
                if success:
                    return success, _resolved, _clauses, None
        return False, solution, clauses, None
