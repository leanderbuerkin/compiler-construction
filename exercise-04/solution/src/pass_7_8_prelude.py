from label import Label
import ast_7_patched as src
import ast_8_riscv as tgt
from register import *
from util.immutable_list import ilist

from register_allocation import RegAllocOutput

def add_prelude_and_conclusion(p: src.Program, reg_alloc: RegAllocOutput, start_label: Label = Label("main"), exit_label: Label = Label("exit")) -> tgt.Program:
    offset = align(16, reg_alloc.offset)
    prefix: tgt.Program = ilist(
        tgt.DGlobal(start_label),
        start_label,
        tgt.IInstr2("addi", sp, sp, -offset),
        tgt.Store(ra, tgt.Offset(sp, offset - 8)),
        tgt.Store(fp, tgt.Offset(sp, offset - 16)),
        tgt.IInstr2("addi", fp, sp, offset),
    )

    _offset = 16
    for r in reg_alloc.callee_saved:
        _offset += 8
        prefix += ilist(tgt.Store(r, tgt.Offset(sp, offset - _offset)))

    p[start_label] = prefix + p[start_label]

    suffix: tgt.Program = ilist(
        tgt.IInstr2("addi", a0, zero, 0),
        tgt.Load(ra, tgt.Offset(fp, -8)),
        tgt.Load(fp, tgt.Offset(fp, -16)),
    )

    _offset = 16
    for r in reg_alloc.callee_saved:
        _offset += 8
        suffix += ilist(tgt.Load(r, tgt.Offset(fp, -_offset)))

    suffix += ilist(
        tgt.IInstr2("addi", sp, sp, offset),
        tgt.Return(),
    )

    p[exit_label] = suffix

    out: tgt.Program = ilist()
    for label, block in p.items():
        if label != start_label:
            out += ilist(label)
        out += block

    return out


def align(alignment: int, n: int) -> int:
    return n if n % alignment == 0 else (n // alignment + 1) * alignment
