import sys
import mxklabs.dimacs


def main():
    dimacs_rules_filename = sys.argv[1]
    dimacs_sudoku_filename = sys.argv[2]
    dimacs_rules = mxklabs.dimacs.read(dimacs_rules_filename)
    dimacs_sudoku = mxklabs.dimacs.read(dimacs_sudoku_filename)
    foo = dimacs_sudoku


main()
