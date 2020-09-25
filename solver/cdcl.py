import copy
import sys
from typing import Set, Dict, List, Tuple, Optional

split = sys.argv[3] if len(sys.argv) >= 4 else 'dlcs'


# noinspection DuplicatedCode
def dp(clauses: List[Set[int]],
       resolved: Dict[int, bool],
       unprocessed: Set[int],
       call_split: bool = True,
       **split_vars) -> Tuple[bool, Dict[int, bool], List[Set[int]], Optional[int]]:
    # noinspection DuplicatedCode
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

    # Test for pure literals.
    unprocessed: Set[int] = set()

    # Copy the clauses, because otherwise the loop will break if we remove items from the iteration.
    for clause in [*clauses]:
        removed: bool = False
        # Remove all clauses that contain a resolved variable.
        for literal in unprocessed and not removed:
            # Remove the whole clause if it contains the resolved literal (therefore the clause resolves to True).
            if literal in clause:
                clauses.remove(clause)
                removed = True
                continue

            # Remove the opposite literal from the clause, because the instance will resolve to False.
            polar_literal: int = literal * -1
            if polar_literal in clause:
                clause.remove(polar_literal)
                clauses[clauses.index(clause)] = clause
                # Test for empty clauses.
                if len(clause) == 0:
                    return False, resolved, clauses, abs(literal)

        if removed:
            continue

        clause_length: int = len(clause)

        # Test for unit clauses.
        if clause_length == 1:
            clauses.remove(clause)
            literal = [*clause][0]
            # Since there is only one literal left in this clause, we can resolve it to True (called unit propagation).
            if not resolve(literal):
                # We encountered a contradiction.
                return False, resolved, clauses, abs(literal)
            continue

    # There is still something to process, rerun with the current context.
    if len(unprocessed) != 0:
        return dp(clauses, resolved, unprocessed, call_split, **split_vars)

    # Test if there are still unresolved clauses, which means that we're not done yet with parsing.
    elif call_split and len(clauses) != 0:
        # Perform a Split operation.
        return split_cdcl(clauses, resolved)

    # Found a solution!
    return True, resolved, clauses, None


# Conflict-Driven Clause Learning split.
def split_cdcl(clauses: List[Set[int]],
               resolved: Dict[int, bool]) -> Tuple[bool, Dict[int, bool], List[Set[int]]]:
    unresolved: Dict[int, Tuple[List[Set[int]], List[Set[int]]]] = {}

    for clause in clauses:
        for literal in clause:
            variable = abs(literal)
            if variable not in unresolved:
                unresolved[variable] = ([], [])
            unresolved[variable][variable == literal].append(clause - {literal})

    history: List[Tuple[int, Set[int]]] = []
    backtrack = {}
    for literal in [-1, 3, -2, 7]:
        variable = abs(literal)
        polarity = variable == literal

        success, _resolved, _clauses, conflict = dp(clauses, {**resolved, variable: polarity}, {literal}, False)
        new_literals: Set[int] = {*map(
            lambda _variable: _variable if _resolved[_variable] else _variable * -1,
            {*_resolved} - {*resolved}
        )}

        history.append((literal, new_literals))

        # for new_literal in new_literals:
        #     new_variable = abs(new_literal)
        #     new_polarity: bool = new_variable == new_literal
        #     if new_literal not in backtrack:
        #         backtrack[new_literal] = {}
        #     for clause in unresolved[new_variable][new_polarity]:
        #         variables = extract_clause_vars(clause)
        #         if len(variables - set(_resolved)) == 0:
        #             for historic_literals in history:
        #                 backtrack_variables = extract_clause_vars(historic_literals).intersection(variables)
        #                 if len(backtrack_variables) != 0:
        #                     backtrack[new_literal][history.index(historic_literals)] = backtrack_variables
        # continue

    return False, resolved, clauses, None


def extract_clause_vars(clause: Set[int]) -> Set[int]:
    # Get the variable name from all literals in the clause by removing any hyphens.
    return {*map(lambda literal: abs(literal), clause)}


def remove_literal(clause: Set[int], literal: int) -> Set[int]:
    if literal in clause:
        clause.remove(literal)
    return clause


print(dp([
    {1, 4},
    {1, -3, -8},
    {1, 8, 12},
    {2, 11},
    {-7, -3, 9},
    {-7, 8, -9},
    {7, 8, -10},
    {7, 10, -12},
], {}, set()))
