import sys

from tools.get_solver import get_solver, get_order
from tools.printer import print_solution, print_stats

split = sys.argv[1]
input_filename = sys.argv[2]


solver = get_solver(split, input_filename)

success, solution, clauses, conflict = solver.solve(order=get_order(split))
print_solution(success, solution)
print_stats(solver)
