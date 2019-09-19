import copy
import math
import sys
import time
from typing import Set, Dict, List, Union, Tuple

import mxklabs.dimacs
from mxklabs.dimacs import Dimacs

start: float = time.perf_counter()
split = sys.argv[3] if 3 in sys.argv else 'dlcs'


def main(problem_filename: str, solvable_filename: str) -> None:
    globals()['start']: float = time.process_time()
    problem: Dimacs = mxklabs.dimacs.read(problem_filename)
    solved: Dimacs = mxklabs.dimacs.read(solvable_filename)
    # Simply prepend the solvable clauses to problem clauses, because the Davis-Putman algorithm will solve the clauses
    # early on anyway, so there is no need to run the algorithm twice.
    clauses: List[Set[int]] = [*map(lambda clause: {*clause}, solved.clauses + problem.clauses)]

    print("Resolving {} {} clauses".format(solvable_filename, len(clauses)))

    result: Union[bool, Dict[int, bool]] = dp(clauses, {}, set())

    if result:
        positive_vars: List[int] = [*sorted(filter(lambda _variable: result[_variable], result))]
        print("Solution found. {} variables resolved, {} positive vars.".format(len(result), len(positive_vars)))
        sqrt: float = math.sqrt(len(positive_vars))
        if sqrt.is_integer():
            for row in range(int(sqrt)):
                print(positive_vars[:int(sqrt)])
                positive_vars = positive_vars[int(sqrt):]
        else:
            print(positive_vars)
    else:
        print("No solution found.")
    print("Time: {}\n".format(time.process_time() - globals()['start']))


def dp(clauses: List[Set[int]],
       resolved: Dict[int, bool],
       unprocessed: Set[int],
       **split_vars) -> Union[bool, Dict[int, bool]]:
    if time.process_time() - globals()['start'] > 30:
        raise Exception("Time of 30 seconds exceeded.")

    def resolve(_literal: int) -> bool:
        _variable: int = abs(_literal)
        _polarity: bool = _variable == _literal
        # Only write to resolved and unprocessed when necessary.
        if _variable not in resolved:
            resolved[_variable]: bool = _polarity
            unprocessed.add(_literal)
        # We encountered a contradiction.
        elif resolved[_variable] != _polarity:
            return False
        return True

    # Remove all clauses that contain a resolved variable.
    for literal in unprocessed:
        polar_literal: int = literal * -1
        # Remove the whole clause if it contains the resolved literal (therefore the clause resolves to True).
        clauses: List[Set[int]] = [*filter(lambda _clause: literal not in _clause, clauses)]
        # Remove the opposite literal from the clause, because the instance will resolve to False.
        clauses: List[Set[int]] = [*map(lambda _clause: remove_literal(_clause, polar_literal), clauses)]

    # Test for pure literals.
    pure_literals: Dict[int, int] = {}
    rejected_variables: Set[int] = set()
    unprocessed: Set[int] = set()

    # Copy the clauses, because otherwise the loop will break if we remove items from the iteration.
    for clause in [*clauses]:
        clause_length: int = len(clause)
        # Test for empty clauses.
        # @TODO Fix DIMACS parser that it won't drop empty clauses from the input file.
        if clause_length == 0:
            # This empty clause is likely to be caused by a contradiction that occurred when all literals were removed
            # from this clause during the processing of the newly resolved variables.
            return False

        # Test for tautologies.
        if clause_length != len(extract_clause_vars(clause)):
            # Drop the clause, because it will resolve to true, regardless of the value of its variables.
            clauses.remove(clause)
            continue

        # Test for unit clauses.
        if clause_length == 1:
            clauses.remove(clause)
            # Since there is only one literal left in this clause, we can resolve it to True (called unit propagation).
            if not resolve([*clause][0]):
                # We encountered a contradiction.
                return False
            continue

        # Keep track of all pure literals that we may encounter.
        for literal in clause:
            variable: int = abs(literal)
            # Keep track if this literal was marked as not pure, so we don't have to probe it again.
            if variable in rejected_variables:
                continue
            polar_literal: int = literal * -1
            # The current literal is not pure, because its opposite value exists.
            if polar_literal in pure_literals:
                pure_literals.pop(polar_literal)
                rejected_variables.add(variable)
            else:
                pure_literals[variable]: bool = literal

    # Test for pure literals.
    for variable in pure_literals:
        if not resolve(pure_literals[variable]):
            # We encountered a contradiction.
            return False

    # There is still something to process, rerun with the current context.
    if len(unprocessed) != 0:
        return dp(clauses, resolved, unprocessed, **split_vars)

    # Test if there are still unresolved clauses, which means that we're not done yet with parsing.
    elif len(clauses) != 0:
        # Perform a Split operation.
        return {
            'cdcl': split_cdcl,
            'dlcs': split_dlcs,
        }[split](clauses, resolved, **split_vars)

    # Found a solution!
    return resolved


# Conflict-Driven Clause Learning split.
def split_cdcl(clauses: List[Set[int]],
               resolved: Dict[int, bool],
               extra: List[int]) -> Union[bool, Dict[int, bool]]:
    # while True:

    # implication_graph: Dict[int, Set[int]] = {}
    # implication_graph: Dict[int, Set[int]] = {}
    # branching_literal: int = clauses.pop().pop()
    # polar_literal: int = branching_literal * -1
    # if branching_literal not in implication_graph:
    #     implication_graph[branching_literal] = set()
    # for clause in clauses:
    #     if len(clause) == 2 and polar_literal in clause:
    #         clause.remove(polar_literal)
    #         implication_graph[branching_literal].add(clause.pop())
    # # unresolved = unresolved.union(extract_clause_vars(clause))
    return False


# Dynamic Largest Combined Sum split.
def split_dlcs(clauses: List[Set[int]],
               resolved: Dict[int, bool],
               backtrace: List[int] = None,
               stack: List[int] = None) -> Union[bool, Dict[int, bool]]:
    if backtrace is None:
        backtrace = []
    if stack is None:
        stack = []

    # Get all variables from the clauses.
    unresolved_neg: Dict[int, int] = {}
    unresolved_pos: Dict[int, int] = {}
    unresolved_frq: Dict[int, int] = {}
    for clause in clauses:
        for literal in clause:
            if literal in backtrace:
                continue
            variable: int = abs(literal)
            polarity: bool = literal == variable
            if variable not in unresolved_frq:
                unresolved_neg[variable] = 0
                unresolved_pos[variable] = 0
                unresolved_frq[variable] = 0
            (unresolved_pos if polarity else unresolved_neg)[variable] += 1
            unresolved_frq[variable] += 1

    # We will resolve the open variables in order of total frequency (both negative and positive literals combined).
    sort: List[Tuple[int, int]] = [*sorted(unresolved_frq.items(), key=lambda x: x[1], reverse=True)]
    # for variable in sorted(unresolved_frq):
    for variable, frq in sort:
        for direction in [True, False]:
            polarity: bool = direction if unresolved_pos[variable] > unresolved_neg[variable] else not direction
            literal: int = variable if polarity else variable * -1
            # Re-run the algorithm with a new literal value.
            result: Union[bool, Dict[int, bool]] = dp(
                # Do a deep copy, because otherwise it gets stuck with clause simplifications from previous attempts.
                copy.deepcopy(clauses),
                {variable: polarity, **resolved},
                {literal},
                backtrace=[*backtrace],
                stack=[*stack, literal]
            )
            if result:
                return result
            # Append the current literal to the backtrace, so that it won't get scanned again.
            backtrace.append(literal)
    return False


def extract_clause_vars(clause: Set[int]) -> Set[int]:
    # Get the variable name from all literals in the clause by removing any hyphens.
    return {*map(lambda literal: abs(literal), clause)}


def remove_literal(clause: Set[int], literal: int) -> Set[int]:
    if literal in clause:
        clause.remove(literal)
    return clause


# main(sys.argv[1], sys.argv[2])
for i in range(1000):
    try:
        main(sys.argv[1], 'input/encoded/1000sudokus-{}.cnf'.format(str(i).rjust(4, '0')))
    except Exception as e:
        print("Exception: ", str(e), "\n")
