import copy
import sys
import timeit
from typing import Set, Dict, List

import mxklabs.dimacs

start = timeit.default_timer()
NEG = 'negative'
POS = 'positive'
FRQ = 'frequency'


def main():
    problem_filename = sys.argv[1]
    solvable_filename = sys.argv[2]
    problem = mxklabs.dimacs.read(problem_filename)
    solved = mxklabs.dimacs.read(solvable_filename)

    # Simply prepend the solvable clauses to problem clauses, because the Davis-Putman algorithm will solve the clauses
    # early on anyway, so there is no need to run the algorithm twice.
    clauses: List[Set[int]] = [*map(lambda clause: {*clause}, solved.clauses + problem.clauses)]
    resolved: Dict[int, bool] = {}
    unprocessed: Set[int] = set()

    print("{} clauses".format(len(clauses)))

    result: bool = dp(clauses, resolved, unprocessed, len(clauses), list())

    if result:
        print("Solution found. {} variables resolved."
              .format(len(resolved)))
    else:
        print("No solution found. {} variables resolved."
              .format(len(resolved)))


def dp(clauses: List[Set[int]],
       resolved: Dict[int, bool],
       unprocessed: Set[int],
       prev_num_clauses: int,
       depth):
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
        if clause_length == 0:
            return False

        # Test for tautologies.
        if clause_length != len(extract_clause_vars(clause)):
            clauses.remove(clause)
            continue

        # Test for unit clauses.
        if clause_length == 1:
            clauses.remove(clause)
            literal: int = clause.pop()
            variable: int = abs(literal)
            polarity: bool = variable == literal
            if variable not in resolved:
                resolved[variable] = polarity
                unprocessed.add(literal)
            # We encountered a contradiction.
            elif resolved[variable] != polarity:
                return False
            continue

        # Test for pure literals.
        for literal in clause:
            variable = abs(literal)
            if variable in rejected_variables:
                continue

            polar_literal = literal * -1
            if polar_literal in pure_literals:
                pure_literals.pop(polar_literal)
                rejected_variables.add(variable)
            else:
                pure_literals[variable] = variable == literal

    for variable in pure_literals:
        if variable not in resolved:
            resolved[variable] = pure_literals[variable]
            unprocessed.add(variable if pure_literals[variable] == abs(pure_literals[variable]) else variable * -1)
        elif resolved[variable] != pure_literals[variable]:
            return False

    num_clauses = len(clauses)
    if len(unprocessed) == 0:
        # Test for an empty set of clauses.
        if num_clauses == 0:
            return True
        elif num_clauses == prev_num_clauses:
            unresolved: Dict[str, Dict[int, int]] = extract_vars(clauses)
            sort = sorted(unresolved[FRQ].items(), key=lambda x: x[1], reverse=True)
            for direction in [True]:
                for variable, frequency in sort:
                    # polarity = direction if unresolved[POS][variable] < unresolved[NEG][variable] else not direction
                    polarity = direction
                    literal = variable if polarity else variable * -1

                    print("Stack {} Trying {}".format(depth, literal))
                    if dp(copy.deepcopy(clauses), {variable: polarity, **resolved}, {literal}, num_clauses, [*depth, literal]):
                        return True
            return False

    return dp(clauses, resolved, unprocessed, num_clauses, depth)


def extract_vars(clauses: List[Set[int]]):
    result: Dict[str, Dict[int, int]] = {
        NEG: {},
        POS: {},
        FRQ: {},
    }
    for clause in clauses:
        for literal in clause:
            variable = abs(literal)
            polarity = literal == variable
            if variable not in result[FRQ]:
                result[NEG][variable] = 0
                result[POS][variable] = 0
                result[FRQ][variable] = 0
            result[POS if polarity else NEG][variable] += 1
            result[FRQ][variable] += 1
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
