import csv
import sys

from tools.get_solver import get_solver, get_order
from tools.printer import print_solution, print_stats

prefix_filename: str = sys.argv[1]
n: int = int(sys.argv[2])
offset: int = int(sys.argv[3]) if len(sys.argv) >= 4 else 0
splits = sys.argv[4].split(",") if len(sys.argv) >= 5 else [
    'fifo', 'fifo__reversed', 'fifo__negative_only', 'fifo__positive_only',
    'dlcs', 'dlcs__reversed', 'dlcs__negative_only', 'dlcs__positive_only',
    'dlis', 'dlis__reversed', 'dlis__negative_only', 'dlis__positive_only',
]

end = offset + n

with open("output/stats-{}-{}.csv".format(offset, end), mode='w', newline='') as stats_file:
    stats = csv.writer(stats_file)

    stats.writerow([
        'sudoku',
        'split',
        'time',
        'dp_calls',
        'literal_iterations',
        'literal_searches',
        'number_known',
        'lowest_freq',
        'highest_freq'
    ])
    stats_file.flush()

    print("Processing Sudoku {} to {}".format(str(offset), str(end)))
    for i in range(offset, end):
        print("Sudoku: {}".format(str(i)))
        input_filename = "{}-{}.cnf".format(prefix_filename, str(i).zfill(4))

        for split in splits:
            print("Split:  {}".format(split))
            solver = get_solver(split, input_filename, True, False)

            try:
                success, solution, clauses, conflict = solver.solve(order=get_order(split))
                print_solution(success, solution)
            except Exception as e:
                print(e)

            print_stats(solver)

            stats.writerow([
                i,
                split,
                solver.end - solver.start,
                solver.dp_calls,
                solver.literal_iterations,
                solver.literal_searches,
                len(solver.known),
                solver.frequencies[-1][1],
                solver.frequencies[1][1],
            ])
            stats_file.flush()





