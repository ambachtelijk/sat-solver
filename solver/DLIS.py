import copy
from typing import List, Dict, Set, Tuple, Optional
from solver.Solver import Solver


class DLIS(Solver):
    """Dynamic Largest Individual Sum split."""

    # noinspection PyMethodOverriding, DuplicatedCode
    def _split(
            self,
            clauses: List[Set[int]],
            solution: Dict[int, bool],
            order: List[bool]
    ) -> Tuple[bool, Dict[int, bool], List[Set[int]], Optional[int]]:
        # Get all variables from the clauses.
        unresolved_variables = {
            variable for variable, polarity in solution.items()
            if polarity is None
        }
        frequencies: Dict[int, int] = {}
        for clause in clauses:
            for literal in clause:
                variable = abs(literal)

                if variable not in unresolved_variables:
                    continue

                if literal not in frequencies:
                    frequencies[literal] = 0

                if literal * -1 not in frequencies:
                    # This should never happen, because it indicates the existence of a pure literal.
                    frequencies[literal * -1] = 0
                frequencies[literal] += 1

        # We will resolve the open variables in order of total frequency (both negative and positive literals
        # combined).
        sort: List[Tuple[int, int]] = [*sorted(frequencies.items(), key=lambda x: x[1], reverse=True)]

        for direction in order:
            for literal, frq in sort:
                _literal = literal if frequencies[literal] > frequencies[literal * -1] and direction else literal * -1

                # Make a deep copy, because otherwise it gets stuck with clause simplifications from previous
                # attempts.
                clauses_copy = copy.deepcopy(clauses)
                solution_copy = {**solution}

                # Add the literal to the solution.
                if not self._resolve(_literal, clauses_copy, solution_copy):
                    continue

                # Re-run the DP algorithm with the new literal value added to the solution.
                success, _solution, _clauses, conflict = self._dp(clauses_copy, solution_copy, order=order)

                if success:
                    return success, _solution, _clauses, None

        return False, solution, clauses, None
