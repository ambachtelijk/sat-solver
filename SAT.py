import sys
import timeit
from typing import Set, Dict, List

import mxklabs.dimacs

start = timeit.default_timer()


def main():
    problem_filename = sys.argv[1]
    solvable_filename = sys.argv[2]
    problem = mxklabs.dimacs.read(problem_filename)
    solved = mxklabs.dimacs.read(solvable_filename)

    # Simply prepend the solvable clauses to problem clauses, because the Davis-Putman algorithm will solve the clauses
    # early on anyway, so there is no need to run the algorithm twice.
    clauses: List[Set[int]] = [*map(lambda clause: {*clause}, solved.clauses + problem.clauses)]
    resolved: Dict[int, bool] = {}
    unresolved: Set[int] = extract_vars(clauses)
    unprocessed: Set[int] = set()
    print("{} variables extracted. {} clauses".format(len(unresolved), len(clauses)))
    result: bool = dp(clauses, resolved, unresolved, unprocessed, len(clauses))

    if result:
        print("Solution found. {} variables resolved, {} variables unresolved."
              .format(len(resolved), len(unresolved)))
    else:
        print("No solution found. {} variables resolved, {} variables unresolved. {} clauses remaining."
              .format(len(resolved), len(unresolved), len(clauses)))


def dp(clauses: List[Set[int]], resolved: Dict[int, bool], unresolved: Set[int], unprocessed: Set[int],
       num_clauses: int):
    # Remove all clauses that contain a resolved variable.
    for literal in unprocessed:
        polar_literal = literal * -1
        # Remove the whole clause if it contains the resolved literal (therefore the clause resolves to True).
        clauses = filter(lambda _clause: literal not in _clause, clauses)
        # Remove the opposite literal from the clause, because the instance will resolve to False.
        clauses = [*map(lambda _clause: remove_literal(_clause, polar_literal), clauses)]

    # Test for pure literals
    pure_literals: Dict[int, bool] = {}
    rejected_variables: Set[int] = set()
    unprocessed: Set[int] = set()

    # Copy the clauses, because otherwise the loop will break if we remove items from the iteration.
    for clause in clauses.copy():
        clause_length: int = len(clause)
        # Test for empty clauses.
        # @todo fix DIMACS parser that it won't drop empty clauses
        if len(clause) == 0:
            return False

        # Test for tautologies.
        if clause_length != len(extract_clause_vars(clause)):
            clauses.remove(clause)
            continue

        # Test for unit clauses.
        if clause_length == 1:
            literal: int = clause.pop()
            variable: int = abs(literal)
            polarity: bool = variable == literal
            if variable not in resolved:
                resolved[variable] = polarity
                unresolved.remove(variable)
                unprocessed.add(literal)
            elif resolved[variable] != polarity:
                return False
            clauses.remove(clause)
            continue

        # Test for pure literals.
        for literal in clause:
            variable = abs(literal)
            if variable in rejected_variables:
                continue

            polar_literal = literal * 1
            if polar_literal in pure_literals:
                pure_literals.pop(polar_literal)
                rejected_variables.add(variable)
            else:
                pure_literals[variable] = variable == literal

    for variable in pure_literals:
        if variable not in resolved:
            resolved[variable] = pure_literals[variable]
            unresolved.remove(variable)
            unprocessed.add(variable if pure_literals[variable] == abs(pure_literals[variable]) else variable * -1)
        elif resolved[variable] != pure_literals[variable]:
            return False

    # len_clauses = len(clauses)
    # len_resolved = len(resolved)
    # len_unresolved = len(unresolved)
    # Test for an empty set of clauses.
    if len(pure_literals) == 0:
        if len(clauses) == 0:
            return True
        elif len(clauses) == num_clauses:
            for variable in resolved:
                if resolved[variable]:
                    print(variable)
            return False
    return dp(clauses, resolved, unresolved, unprocessed, len(clauses))


def extract_vars(clauses: List[Set[int]]):
    result: Set[int] = set()
    for clause in clauses:
        result = result.union(extract_clause_vars(clause))
    return result


def extract_clause_vars(clause: Set[int]):
    # Get the variable name from all literals in the clause by removing any hyphens.
    return {*map(lambda literal: abs(literal), clause)}


def remove_literal(clause: Set[int], literal: int):
    if literal in clause:
        clause.remove(literal)
    return clause


main()
stop = timeit.default_timer()
print('Time: ', stop - start)
