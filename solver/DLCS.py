import copy
from typing import List, Dict, Set, Tuple, Optional

from solver.Solver import Solver


# Dynamic Largest Combined Sum split.
class DLCS(Solver):
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
        unresolved_neg: Dict[int, int] = {}
        unresolved_pos: Dict[int, int] = {}
        unresolved_frq: Dict[int, int] = {}
        for clause in clauses:
            for literal in clause:
                variable = abs(literal)
                polarity = variable == literal
                if solution[variable] is not None or literal in backtrace or literal * -1 in backtrace:
                    continue
                if variable not in unresolved_frq:
                    unresolved_neg[variable] = 0
                    unresolved_pos[variable] = 0
                    unresolved_frq[variable] = 0
                (unresolved_pos if polarity else unresolved_neg)[variable] += 1
                unresolved_frq[variable] += 1

        # We will resolve the open variables in order of total frequency (both negative and positive literals combined).
        sort: List[Tuple[int, int]] = [*sorted(unresolved_frq.items(), key=lambda x: x[1], reverse=True)]

        for direction in order:
            for variable, frq in sort:
                polarity: bool = direction if unresolved_pos[variable] > unresolved_neg[variable] else not direction
                literal: int = variable if polarity else variable * -1
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
