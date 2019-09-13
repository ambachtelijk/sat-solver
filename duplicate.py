import sys
from math import sqrt

import mxklabs.dimacs


def main():
    rules_filename = sys.argv[1]
    sudoku_filename = sys.argv[2]
    rules = mxklabs.dimacs.read(rules_filename)
    sudoku = mxklabs.dimacs.read(sudoku_filename)

    sudoku_vars = initialize_vars(sudoku.clauses)
    for clause in sudoku.clauses:
        # Test for unit clauses.
        if len(clause) == 1:
            value = clause[0]
            variable = abs(value)
            # Set the variable to 1 if the value does not contain a hyphen, and therefore equals to its absolute value.
            sudoku_vars[variable] = check_variable(sudoku_vars, variable, 1 if variable == value else 0)

    foo = sudoku_vars


def check_variable(variables, key, value):
    if variables[key] != -1 and variables[key] != value:
        raise Exception("Variable {} is a contradiction".format(key))
    return value


def dp(clause, unresolved_vars, resolved_vars):
    return clause


def initialize_vars(clauses):
    result = set()
    for clause in clauses:
        # The variables in this clause.
        variables = list()

        # Get the variable name from all literals in the clause by removing any hyphens.
        for literal in clause:
            variables.append(abs(literal))

        # The transformation to set will deduplicate the concatenated list.
        result = set(list(result) + variables)

    # Convert the result set to a dict. Each variable can take one of these values:
    # -1 this variable has not been resolved yet
    #  0 this variable resolved to FALSE
    #  1 this variable resolved to TRUE
    return dict.fromkeys(result, -1)


# Converts a sudoku.txt file into clauses
def convert_sudoku(sudoku_file):
    # Opens the file and determines the sudoku size
    file = open(sudoku_file, "r")
    begin_position = file.tell()
    sudoku_size = sqrt(len(file.readline()) - 1)
    file.seek(begin_position)

    # Determines if sudoku works number bigger than 0 to 9
    bigger_than_nine = False
    if sudoku_size > 9:
        bigger_than_nine = True
    alfabet_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    # List to store the sudoku's in
    list_sudokus = []

    # Iterates over every line, creating a sudoku of each line in the file
    for line in file:
        if bigger_than_nine:
            counter = 10000
        else:
            counter = 100
        sudoku_line_count = 0

        # List to store the clauses in
        clause_list = list()

        # Iterates over every character in the line, making it a clause if it's a number
        for character in line:
            if bigger_than_nine:
                counter += 100
            else:
                counter += 10
            sudoku_line_count += 1

            # Determines if it's a useable clause
            if character != "." and character != '\n':
                if character in alfabet_list:
                    clause = (ord(character.lower()) - 86) + counter
                else:
                    clause = int(character) + counter
                clause_list.append(clause)

            # Manages which vertical line the number is on
            if sudoku_line_count == sudoku_size:
                if bigger_than_nine:
                    counter += 10000
                    counter -= 100 * sudoku_size
                else:
                    counter += 100
                    counter -= 10 * sudoku_size
                sudoku_line_count = 0

        # Stores the result in a dict and adds to list of sudoku's
        result = dict.fromkeys(clause_list, -1)
        list_sudokus.append(result)


main()
