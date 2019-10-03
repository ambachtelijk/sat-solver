import copy
import math
import os
import sys
import time
import traceback
from typing import Set, Dict, List, Tuple, IO, Optional

import mxklabs.dimacs
from mxklabs.dimacs import Dimacs

start: float = time.perf_counter()
split = sys.argv[3] if len(sys.argv) >= 4 else 'dlcs'


def main(problem_filename: str, solvable_filename: str) -> None:
    globals()['start']: float = time.process_time()
    problem: Dimacs = mxklabs.dimacs.read(problem_filename)
    solved: Dimacs = mxklabs.dimacs.read(solvable_filename)
    # Simply prepend the solvable clauses to problem clauses, because the Davis-Putman algorithm will solve the clauses
    # early on anyway, so there is no need to run the algorithm twice.
    clauses: List[Set[int]] = [*map(lambda _clause: {*_clause}, solved.clauses + problem.clauses)]

    print("Resolving {} {} clauses".format(solvable_filename, len(clauses)))

    solution = dict.fromkeys(sorted({abs(literal) for clause in clauses for literal in clause}), None)
    unprocessed = set()
    success = True
    # Remove all tautologies.
    clauses = [clause for clause in clauses if len(clause) == len(extract_clause_vars(clause))]
    for clause in [*clauses]:
        # Test for unit clauses.
        if len(clause) == 1:
            clauses.remove(clause)
            literal = [*clause][0]
            # Since there is only one literal left in this clause, we can resolve it to True (called unit propagation).
            if not resolve(literal, solution, unprocessed):
                # We encountered a contradiction.
                success = False
                break

    # Test for empty clauses.
    # @TODO Fix DIMACS parser that it won't drop empty clauses from the input file.
    if clauses.count(set()) == 0:
        try:
            success, solution, clauses, conflict = dp(clauses, solution, unprocessed)
        except Exception:
            tb = traceback.format_exc()
            print(tb)
            exit()

    if success:
        positive_vars: List[int] = [*sorted(filter(lambda _variable: solution[_variable], solution))]
        print("Solution found. {} variables solution, {} positive vars.".format(len(solution), len(positive_vars)))
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


# noinspection DuplicatedCode
def dp(clauses: List[Set[int]],
       solution: Dict[int, Optional[bool]],
       unprocessed: Set[int],
       call_split: bool = True,
       **split_vars) -> Tuple[bool, Dict[int, bool], List[Set[int]], Optional[int]]:
    # if time.process_time() - globals()['start'] > 30:
    #     raise Exception("Time of 30 seconds exceeded.")

    # # Test for pure literals.
    # pure_literals: Dict[int, int] = {}
    # rejected_variables: Set[int] = set()
    new_unprocessed: Set[int] = set()

    # Copy the clauses, because otherwise the loop will break if we remove items from the iteration.
    for clause in [*clauses]:
        removed: bool = False
        # Remove all clauses that contain a resolved variable.
        for literal in unprocessed:
            # Remove the whole clause if it contains the resolved literal (therefore the clause resolves to True).
            if literal in clause:
                clauses.remove(clause)
                # removed = True
                break

            # Remove the opposite literal from the clause, because the instance will resolve to False.
            polar_literal: int = literal * -1
            if polar_literal in clause:
                clause.remove(polar_literal)
                clauses[clauses.index(clause)] = clause
                # Test for empty clauses.
                if len(clause) == 0:
                    return False, solution, clauses, abs(literal)

                # Test for unit clauses.
                if len(clause) == 1:
                    clauses.remove(clause)
                    unit_literal = [*clause][0]
                    # Since there is only one literal left in this clause, we can resolve it to True (called unit
                    # propagation).
                    if not resolve(unit_literal, solution, new_unprocessed):
                        # We encountered a contradiction.
                        return False, solution, clauses, abs(unit_literal)
        # if removed:
        #     continue
    #
    #     # Keep track of all pure literals that we may encounter.
    #     for literal in clause:
    #         variable: int = abs(literal)
    #         # Keep track if this literal was marked as not pure, so we don't have to probe it again.
    #         if variable in rejected_variables:
    #             continue
    #         polar_literal: int = literal * -1
    #         # The current literal is not pure, because its opposite value exists.
    #         if polar_literal in pure_literals:
    #             pure_literals.pop(polar_literal)
    #             rejected_variables.add(variable)
    #         else:
    #             pure_literals[variable]: int = literal
    #
    # # Test for pure literals.
    # for variable in pure_literals:
    #     if not resolve(pure_literals[variable]):
    #         # We encountered a contradiction.
    #         return False, resolved, clauses, abs(pure_literals[variable])

    # There is still something to process, rerun with the current context.
    if len(new_unprocessed) != 0:
        return dp(clauses, solution, new_unprocessed, call_split, **split_vars)

    # Test if there are still unresolved clauses, which means that we're not done yet with parsing.
    elif call_split and len(clauses) != 0:
        # Perform a Split operation.
        return {
            'cdcl': split_cdcl,
            'dlcs': split_dlcs,
        }[split](clauses, solution, **split_vars)

    # Found a solution!
    return True, solution, clauses, None


# Conflict-Driven Clause Learning split.
def split_cdcl(clauses: List[Set[int]],
               resolved: Dict[int, bool]) -> Tuple[bool, Dict[int, bool], List[Set[int]], Optional[int]]:
    unresolved: Dict[int, Tuple[List[Set[int]], List[Set[int]]]] = {}
    return False, resolved, clauses, None


# Dynamic Largest Combined Sum split.
def split_dlcs(clauses: List[Set[int]],
               solution: Dict[int, bool],
               backtrace: Set[int] = None,
               stack: List[int] = None) -> Tuple[bool, Dict[int, bool], List[Set[int]], Optional[int]]:
    if backtrace is None:
        backtrace = set()
    if stack is None:
        stack = []

    # We will resolve the open variables in order of total frequency (both negative and positive literals combined).
    print(stack)
    for variable, polarity in solution.items():
        if polarity is not None or variable in backtrace or variable * -1 in backtrace:
            continue

        for direction in [True]:
            # polarity: bool = direction if unresolved_pos[variable] < unresolved_neg[variable] else not direction
            literal: int = variable if direction else variable * -1
            # Append the current literal to the backtrace, so that it won't get scanned again.
            backtrace.add(literal)

            # Re-run the algorithm with a new literal value.
            success, _resolved, _clauses, conflict = dp(
                # Do a deep copy, because otherwise it gets stuck with clause simplifications from previous attempts.
                copy.deepcopy(clauses),
                {**solution, variable: direction},
                {literal},
                backtrace={*backtrace},
                stack=[*stack, literal]
            )
            if success:
                return success, _resolved, _clauses, None
    return False, solution, clauses, None


# Uncomment to test code
# test_dict = {111: True, 112: True, 113: False, 567: True, 783: False}
# path = 'C:\Studie Projecten\SAT Solver\output'
# Writes an output file in DIMACS format
def write_dimacs(output_directory: str,
                 filename_out: str,
                 solution: Dict[int, bool]):
    file_out: str = os.path.join(output_directory, filename_out)
    output_file: IO = open(file_out, 'w')
    output_file.write("p cnf {} {}\n".format(str(max(solution)), str(len(solution))))

    # Writes every element of dict in new line of output file
    for clause_out in solution:
        if not solution[clause_out]:
            clause_out *= -1
        output_file.write("{} 0\n".format(str(clause_out)))

    output_file.close()


def resolve(_literal: int, _resolved: Dict[int, Optional[bool]], _unprocessed: Set[int]) -> bool:
    _variable: int = abs(_literal)
    _polarity: bool = _variable == _literal
    # Only write to resolved and unprocessed when necessary.
    if _resolved[_variable] is None:
        _resolved[_variable]: bool = _polarity
        _unprocessed.add(_literal)
    # We encountered a contradiction.
    elif _resolved[_variable] != _polarity:
        return False
    return True


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
        main('input/rules/sudoku-rules.txt', 'input/encoded/1000sudokus-{}.cnf'.format(str(i).rjust(4, '0'), 'dc'))
    except Exception as e:
        print("Exception: ", str(e), "\n")
