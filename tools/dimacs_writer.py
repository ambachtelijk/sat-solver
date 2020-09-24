# Writes an output file in DIMACS format
import os
from typing import IO, Dict


def write_dimacs(filename_out: str, solution: Dict[int, bool]):
    file_out: str = os.path.join(filename_out)
    output_file: IO = open(file_out, 'w')
    output_file.write("p cnf {} {}\n".format(str(max(solution)), str(len(solution))))

    # Writes every element of dict in new line of output file
    for clause_out in solution:
        if not solution[clause_out]:
            clause_out *= -1
        output_file.write("{} 0\n".format(str(clause_out)))

    output_file.close()
