import collections
import copy
from typing import List, Dict, Set, Tuple, Optional

from solver.Solver import Solver


class MostFrequent(Solver):
    """Most Frequent Last Digit split"""

    # noinspection PyMethodOverriding,DuplicatedCode
    def _split(
            self,
            clauses: List[Set[int]],
            solution: Dict[int, bool],
            order: List[bool],
            reverse: bool = False
    ) -> Tuple[bool, Dict[int, bool], List[Set[int]], Optional[int]]:
        most_common = collections.Counter([
            variable % 10 for variable, polarity in solution.items()
            if polarity is True
        ]).most_common()
        rankings = dict((frequency[0], ranking) for ranking, frequency in enumerate(most_common))

        unresolved_variables = [variable for variable, polarity in solution.items() if polarity is None]
        unresolved_variables.sort(
            key=lambda variable: rankings[variable % 10] if variable % 10 in rankings else 10,
            reverse=reverse
        )

        for direction in order:
            for variable in unresolved_variables:
                literal: int = variable if direction else variable * -1

                # Make a deep copy, because otherwise it gets stuck with clause simplifications from previous
                # attempts.
                clauses_copy = copy.deepcopy(clauses)
                solution_copy = {**solution}

                # Add the literal to the solution.
                if not self._resolve(literal, clauses_copy, solution_copy):
                    continue

                # Re-run the DP algorithm with the new literal value added to the solution.
                success, _solution, _clauses, conflict = self._dp(clauses_copy, solution_copy, order=order)

                if success:
                    return success, _solution, _clauses, None

        return False, solution, clauses, None
