import copy
import sys
import timeit
from typing import Set, Dict, List

import mxklabs.dimacs

start = timeit.default_timer()
NEG = 'negative'
POS = 'positive'
FRQ = 'frequency'

problem_filename = sys.argv[1]
solvable_filename = sys.argv[2]
split = sys.argv[3] if 3 in sys.argv else 'dlcs'


def main():
    problem = mxklabs.dimacs.read(problem_filename)
    solved = mxklabs.dimacs.read(solvable_filename)

    # Simply prepend the solvable clauses to problem clauses, because the Davis-Putman algorithm will solve the clauses
    # early on anyway, so there is no need to run the algorithm twice.
    clauses: List[Set[int]] = [*map(lambda clause: {*clause}, solved.clauses + problem.clauses)]
    resolved: Dict[int, bool] = {}
    unprocessed: Set[int] = set()

    print("{} clauses".format(len(clauses)))

    result: bool = dp(clauses, resolved, unprocessed, list())

    if result:
        print("Solution found. {} variables resolved."
              .format(len(resolved)))
    else:
        print("No solution found. {} variables resolved."
              .format(len(resolved)))


def dp(clauses: List[Set[int]],
       resolved: Dict[int, bool],
       unprocessed: Set[int],
       depth):
    def resolve(_literal: int):
        _variable: int = abs(_literal)
        _polarity: bool = _variable == _literal
        # Only write to resolved and unprocessed when necessary.
        if _variable not in resolved:
            resolved[_variable] = _polarity
            unprocessed.add(_literal)
        # We encountered a contradiction.
        elif resolved[_variable] != _polarity:
            return False
        return True

    # Remove all clauses that contain a resolved variable.
    for literal in unprocessed:
        polar_literal = literal * -1
        # Remove the whole clause if it contains the resolved literal (therefore the clause resolves to True).
        clauses = filter(lambda _clause: literal not in _clause, clauses)
        # Remove the opposite literal from the clause, because the instance will resolve to False.
        clauses = [*map(lambda _clause: remove_literal(_clause, polar_literal), clauses)]

    # Test for pure literals
    pure_literals: Dict[int, int] = {}
    rejected_variables: Set[int] = set()
    unprocessed: Set[int] = set()

    # Copy the clauses, because otherwise the loop will break if we remove items from the iteration.
    for clause in [*clauses]:
        clause_length: int = len(clause)
        # Test for empty clauses.
        # @TODO Fix DIMACS parser that it won't drop empty clauses from the input file.
        if clause_length == 0:
            return False

        # Test for tautologies.
        if clause_length != len(extract_clause_vars(clause)):
            clauses.remove(clause)
            continue

        # Test for unit clauses.
        if clause_length == 1:
            clauses.remove(clause)
            if not resolve(clause.pop()):
                return False
            continue

        # Keep track of all pure literals that we may encounter.
        for literal in clause:
            variable = abs(literal)
            # Keep track if this literal was marked as not pure, so we don't have to probe it again.
            if variable in rejected_variables:
                continue
            polar_literal = literal * -1
            # The current literal is not pure, because its opposite value exists.
            if polar_literal in pure_literals:
                pure_literals.pop(polar_literal)
                rejected_variables.add(variable)
            else:
                pure_literals[variable] = literal

    # Test for pure literals.
    for variable in pure_literals:
        if not resolve(pure_literals[variable]):
            return False

    # Test for an empty set of clauses, which means that we're done with the parsing.
    if len(clauses) == 0:
        return True

    # There is still something to process, rerun with the current context.
    elif len(unprocessed) != 0:
        return dp(clauses, resolved, unprocessed, depth)

    # Perform a Split operation.
    return {
        'dlcs': split_dlcs,
    }[split](clauses, resolved, unprocessed, depth)


def split_dlcs(clauses: List[Set[int]],
               resolved: Dict[int, bool],
               unprocessed: Set[int],
               depth):
    unresolved: Dict[str, Dict[int, int]] = extract_vars(clauses)
    sort = sorted(unresolved[FRQ].items(), key=lambda x: x[1], reverse=True)
    for direction in [True]:
        for variable, frequency in sort:
            # polarity = direction if unresolved[POS][variable] < unresolved[NEG][variable] else not direction
            polarity = direction
            literal = variable if polarity else variable * -1

            print("Stack {} Trying {}".format(depth, literal))
            # We must do a deep copy, because otherwise we'll get stuck with the clauses from previous attempts.
            if dp(copy.deepcopy(clauses), {variable: polarity, **resolved}, {literal}, [*depth, literal]):
                return True
    return False


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
