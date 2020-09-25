import os
import sys

from tools.dimacs_writer import write_dimacs
from tools.get_solver import get_solver, get_order
from tools.printer import print_solution, print_stats

splits = {'-S1': 'fifo__positive_only', '-S2': 'mfld__positive_only', '-S3': 'dlis__positive_only', '-S4': 'dcls__positive_only'}
if sys.argv[1] not in splits:
    print("Value of first argument is '{}', '-S1' '-S2', '-S3' or '-S4' expected.".format(sys.argv[1]))
elif not os.path.exists(sys.argv[2]):
    print("File from second argument does not exist: '{}'".format(sys.argv[2]))
else:
    split = splits[sys.argv[1]]
    input_filename = sys.argv[2]

    try:
        print("Solving '{}' with heuristic '{}'.".format(input_filename, split))
        solver = get_solver(split, input_filename)
        success, solution, clauses, conflict = solver.solve(order=get_order(split))
        if success:
            write_dimacs(input_filename + '.out', solution)

        print_solution(success, solution)
        print_stats(solver)
    except Exception as e:
        print(e)
