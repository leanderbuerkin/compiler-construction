from label import Label
import ast_5_patched as src
import ast_6_riscv as tgt
from register import *
from util.immutable_list import ilist


def add_prelude_and_conclusion(p: src.Program, offset: int) -> tgt.Program:
    # `offset` is the size of the stack frame as calculated by `assign_homes`.
    ...

def align(alignment: int, n: int) -> int:  
    return n if n % alignment == 0 else (n // alignment + 1) * alignment
