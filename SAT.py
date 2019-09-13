import sys

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


main()
