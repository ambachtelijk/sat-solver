import copy
from typing import List, Dict, Set, Tuple, Optional
from solver.Solver import Solver


class DLCS(Solver):
    """Dynamic Largest Combined Sum split."""

    # noinspection PyMethodOverriding, DuplicatedCode
    def _split(
            self,
            clauses: List[Set[int]],
            solution: Dict[int, bool],
            order: List[bool]
    ) -> Tuple[bool, Dict[int, bool], List[Set[int]], Optional[int]]:
        # Get all variables from the clauses.
        # Get all variables from the clauses.
        unresolved_variables = {
            variable for variable, polarity in solution.items()
            if polarity is None
        }
        frequencies_neg: Dict[int, int] = {}
        frequencies_pos: Dict[int, int] = {}
        frequencies: Dict[int, int] = {}
        for clause in clauses:
            for literal in clause:
                variable = abs(literal)
                polarity = variable == literal

                if variable not in unresolved_variables:
                    continue

                if variable not in frequencies:
                    frequencies_neg[variable] = 0
                    frequencies_pos[variable] = 0
                    frequencies[variable] = 0
                (frequencies_pos if polarity else frequencies_neg)[variable] += 1
                frequencies[variable] += 1

        # We will resolve the open variables in order of total frequency (both negative and positive literals combined).
        sort: List[Tuple[int, int]] = [*sorted(frequencies.items(), key=lambda x: x[1], reverse=True)]

        for direction in order:
            for variable, frq in sort:
                _literal = variable if frequencies_pos[variable] > frequencies_neg[variable] and direction else variable * -1

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
