import math
from typing import List

from solver.Solver import Solver


def print_solution(success: bool, solution):
    if success:
        positive_vars: List[int] = [*sorted(filter(lambda _variable: solution[_variable], solution))]
        print("Solution found. {} variables solution, {} positive vars.".format(len(solution), len(positive_vars)))

        sqrt: float = math.sqrt(len(positive_vars))
        if sqrt.is_integer():
            for row in range(int(sqrt)):
                print(positive_vars[:int(sqrt)])
                positive_vars = positive_vars[int(sqrt):]
        else:
            print(positive_vars)
    else:
        print("No solution found.")


def print_stats(solver: Solver):
    print("Time: {}\nDP calls: {}\nLiteral iterations: {}\nLiteral searches: {}\n".format(
        solver.end - solver.start,
        solver.dp_calls,
        solver.literal_iterations,
        solver.literal_searches
    ))
