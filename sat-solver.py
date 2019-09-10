import sys

from sympy.logic.utilities.dimacs import load_file


def main():
    dimacs_filename = sys.argv[1]
    dimacs = load_file(dimacs_filename)
    print("hello, world")
    print(dimacs)


main()
