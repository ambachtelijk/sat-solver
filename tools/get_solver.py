import mxklabs
from typing import List
from mxklabs.dimacs import Dimacs
from solver.DLIS import DLIS
from solver.DLCS import DLCS
from solver.FIFO import FIFO
from solver.MFLD import MFLD

SEPARATOR = "__"


def get_solver(split: str, input_filename: str):
    if SEPARATOR not in split:
        split = split + SEPARATOR
    split, direction = split.split(SEPARATOR)

    try:
        return {
            'fifo': FIFO,
            'dlcs': DLCS,
            'dlis': DLIS,
            'mfld': MFLD,
        }[split](problem=mxklabs.dimacs.read(input_filename))
    except Exception:
        print("Could not read DIMACS file. Please make sure it is compliant with the DIMACS standard.")
        raise


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
