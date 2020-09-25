import math
from typing import List, Dict, Optional


def print_solution(success: bool, solution: Dict[int, Optional[bool]]):
    if success:
        positive_vars: List[int] = [*sorted(filter(lambda variable: solution[variable], solution))]
        print("Solution found with {} variables, of which {} are positive.".format(len(solution), len(positive_vars)))

        size: float = math.sqrt(math.sqrt(len(positive_vars)))
        if size.is_integer():
            print_sudoku(solution, int(size) ** 2)
        else:
            print(positive_vars)
    else:
        print("No solution found.")


def print_stats(solver):
    print("Time: {}\nDP calls: {}\nSplit calls: {}\nSolution attempts: {}".format(
        solver.end - solver.start,
        solver.dp_calls,
        solver.split_calls,
        solver.solution_attempts
    ))


def print_sudoku(solution: Dict[int, Optional[bool]], size: int = 9):
    print("The input file may be a Sudoku, therefore we're attempting to format the result in a square grid.")
    digits = int(math.log10(size)) + 1

    for row in range(1, size + 1):
        line = ""
        for col in range(1, size + 1):
            cell = "."
            for i in range(1, size + 1):
                variable = int("{}{}{}".format(row, str(col).zfill(digits), str(i).zfill(digits)))
                if variable in solution and solution[variable]:
                    cell = str(i)
                    break
            line = "{} {}".format(line, cell)
        print(line)
    print("")
