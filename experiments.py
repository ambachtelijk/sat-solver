import csv
import sys
from typing import List

from tools.get_solver import get_solver, get_order
from tools.printer import print_solution, print_stats


prefix_input: str = sys.argv[1]
prefix_output: str = sys.argv[2]
splits: List[str] = sys.argv[3].split(",")
n: int = int(sys.argv[4])
offset: int = int(sys.argv[5])
end = offset + n

with open("{}-{}-{}.csv".format(prefix_output, offset, end), mode='w', newline='') as stats_file:
    stats = csv.writer(stats_file)

    stats.writerow([
        'sudoku',
        'split',
        'time',
        'dp_calls',
        'split_calls',
        'solution_attempts',
        'number_known',
        'lowest_freq',
        'highest_freq'
    ])
    stats_file.flush()

    print("Processing Sudoku {} to {}".format(str(offset), str(end)))
    for i in range(offset, end):
        print("Sudoku: {}".format(str(i)))
        input_filename = "{}-{}.cnf".format(prefix_input, str(i).zfill(4))

        for split in splits:
            print("Split:  {}".format(split))
            solver = get_solver(split, input_filename)

            success, solution, clauses, conflict = solver.solve(order=get_order(split))
            print_solution(success, solution)
            print_stats(solver)

            stats.writerow([
                i,
                split,
                solver.end - solver.start,
                solver.dp_calls,
                solver.split_calls,
                solver.solution_attempts,
                len(solver.known),
                solver.frequencies[-1][1],
                solver.frequencies[0][1],
            ])
            stats_file.flush()
