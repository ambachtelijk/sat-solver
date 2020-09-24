import mxklabs
from typing import List
from mxklabs.dimacs import Dimacs
from solver.DLIS import DLIS
from solver.DLCS import DLCS
from solver.FIFO import FIFO

SEPARATOR = "__"


def get_solver(split: str, input_filename: str, preprocess: bool = True, pure_literals: bool = False):
    if SEPARATOR not in split:
        split = split + SEPARATOR
    split, direction = split.split(SEPARATOR)

    return {
        'fifo': FIFO,
        'dlcs': DLCS,
        'dlis': DLIS,
    }[split](
        problem=mxklabs.dimacs.read(input_filename),
        preprocess=preprocess,
        pure_literals=pure_literals
    )


def get_order(split: str) -> List[bool]:
    if SEPARATOR not in split:
        split = split + SEPARATOR
    split, direction = split.split(SEPARATOR)

    if "reversed" in direction:
        return [False, True]
    elif "positive_only" in direction:
        return [True]
    elif "negative_only" in direction:
        return [False]
    else:
        return [True, False]
