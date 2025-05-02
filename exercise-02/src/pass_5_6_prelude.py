from label import Label
import ast_5_patched as src
import ast_6_riscv as tgt
from register import *
from util.immutable_list import ilist

from register_allocation import RegAllocOutput

def add_prelude_and_conclusion(p: src.Program, reg_alloc: RegAllocOutput) -> tgt.Program:
    offset = align(16, reg_alloc.offset)

    prefix: tgt.Program = ilist(
        tgt.DGlobal(Label("main")),
        Label("main"),
        tgt.Store(ra, tgt.Offset(sp, -8)),
        tgt.Store(fp, tgt.Offset(sp, -16)),
        tgt.IInstr2("addi", fp, sp, 0),
        tgt.IInstr2("addi", sp, sp, -offset),
    )

    suffix: tgt.Program = ilist(
        tgt.IInstr2("addi", a0, zero, 0),
        tgt.IInstr2("addi", sp, sp, offset),
        tgt.Load(ra, tgt.Offset(sp, -8)),
        tgt.Load(fp, tgt.Offset(sp, -16)),
        tgt.Return(),
    )

    return prefix + p + suffix

def align(alignment: int, n: int) -> int:
    return n if n % alignment == 0 else (n // alignment + 1) * alignment
