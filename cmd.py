import sys

from tools.get_solver import get_solver, get_order
from tools.printer import print_solution, print_stats

split_algorithm = sys.argv[1]
input_filename = sys.argv[2]


solver = get_solver(split_algorithm, input_filename, True, False)

try:
    success, solution, clauses, conflict = solver.solve(order=get_order(split_algorithm))
    print_solution(success, solution)
except Exception as e:
    print(e)

print_stats(solver)
