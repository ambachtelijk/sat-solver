from typing import IO, Dict, List
import os


# Uncomment to test code
# test_dict = {111: True, 112: True, 113: False, 567: True, 783: False}
# path = 'C:\Studie Projecten\SAT Solver\output'


# Writes an output file in DIMACS format
def outputFile(output_directory: str,
               filename_out: str,
               resolved_dict: Dict[int, bool]):
    file_out: str = os.path.join(output_directory, filename_out)
    output_file: IO = open(file_out, 'w')
    output_file.write("p cnf {} {}\n".format(str(max(resolved_dict)), str(len(resolved_dict))))

    # Writes every element of dict in new line of output file
    for clause_out in resolved_dict:
        if not resolved_dict[clause_out]:
            clause_out *= -1
        output_file.write("{} 0\n".format(str(clause_out)))

    output_file.close()

# Uncomment to test code
# outputFile(path, 'test_out.txt', test_dict)
