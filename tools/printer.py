import math
from typing import List, Dict, Optional


def print_solution(success: bool, solution: Dict[int, Optional[bool]]):
    if success:
        positive_vars: List[int] = [*sorted(filter(lambda variable: solution[variable], solution))]
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


def print_stats(solver):
    print("Time: {}\nDP calls: {}\n".format(
        solver.end - solver.start,
        solver.dp_calls
    ))


def print_sudoku(solution: Dict[int, Optional[bool]]):
    for row in range(1, 10):
        line = ""
        for col in range(1, 10):
            cell = "."
            for i in range(1, 10):
                variable = int("{}{}{}".format(row, col, i))
                if solution[variable]:
                    cell = str(i)
                    break
            line = "{} {}".format(line, cell)
        print(line)
    print("")
