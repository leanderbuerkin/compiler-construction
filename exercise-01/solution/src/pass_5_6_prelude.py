from label import Label
import ast_5_patched as src
import ast_6_riscv as tgt
from register import *
from util.immutable_list import ilist


def add_prelude_and_conclusion(p: src.Program, offset: int) -> tgt.Program:
    offset = align(16, offset)

    prefix: tgt.Program = ilist(
        tgt.DGlobal(Label("main")),
        Label("main"),
        tgt.IInstr2("addi", sp, sp, -offset),
        tgt.Store(ra, tgt.Offset(sp, offset - 8)),
        tgt.Store(fp, tgt.Offset(sp, offset - 16)),
        tgt.IInstr2("addi", fp, sp, offset),
    )

    suffix: tgt.Program = ilist(
        tgt.IInstr2("addi", a0, zero, 0),
        tgt.Load(ra, tgt.Offset(fp, -8)),
        tgt.Load(fp, tgt.Offset(fp, -16)),
        tgt.IInstr2("addi", sp, sp, offset),
        tgt.Return(),
    )

    return prefix + p + suffix

def align(alignment: int, n: int) -> int:
    return n if n % alignment == 0 else (n // alignment + 1) * alignment
