import ast_4_mem as src
import ast_5_patched as tgt
from register import *
from util.immutable_list import ilist

def patch_instructions(p: src.Program) -> tgt.Program:
    p_out: tgt.Program = ilist()
    for i in p:
        p_out += patch_instruction(i)
    return p_out

def patch_instruction(i: src.Instr) -> tgt.Program:
    out: tgt.Program = ilist()
    match i:
        case src.Move(dst, src_):
            match dst:
                case src.Register(_):
                    rd = dst
                    dst_address = None
                case src.Offset(r, o):
                    rd = t0
                    dst_address = tgt.Offset(r, o)
            match src_:
                case src.Register(_):
                    out += ilist(tgt.RInstr("add", rd, zero, src_))
                case src.Offset(r, o):
                    out += ilist(tgt.Load(rd, tgt.Offset(r, o)))
                case src.Const(c):
                    out += ilist(tgt.IInstr1("li", rd, c))
            if dst_address is not None:
                out += ilist(tgt.Store(t0, dst_address))
        case src.Call(l):
            out += ilist(tgt.Call(l))
        case src.Instr2(op, dst, src1, src2):
            match dst:
                case Register(_):
                    rd = dst
                    dst_address = None
                case src.Offset(r, o):
                    rd = t0
                    dst_address = tgt.Offset(r, o)
            match src1:
                case src.Register(_):
                    rs1 = src1
                case src.Offset(r, o):
                    out += ilist(tgt.Load(t0, tgt.Offset(r, o)))
                    rs1 = t0
                case src.Const(c):
                    out += ilist(tgt.IInstr1("li", t0, c))
                    rs1 = t0
            match src2:
                case src.Register(_):
                    rs2: Register | int = src2
                case src.Offset(r, o):
                    out += ilist(tgt.Load(t1, tgt.Offset(r, o)))
                    rs2 = t1
                case src.Const(c):
                    # Use immediate if constant doesn't need many bits
                    if c < 2**11 and c > -(2**11):
                        rs2 = c
                    # Otherwise load it into a register first, where
                    # the pseudo-instruction `li` will use, e.g. a
                    # combination of addi and shifts to load to
                    # constant piece by piece.
                    else:
                        out += ilist(tgt.IInstr1("li", t1, c))
                        rs2 = t1
            match rs2:
                case int(c):
                    match op:
                        case "add":
                            out += ilist(tgt.IInstr2("addi", rd, rs1, c))
                        case "sub":
                            out += ilist(tgt.IInstr2("addi", rd, rs1, -c))
                case Register(_):
                    out += ilist(tgt.RInstr(op, rd, rs1, rs2))

            if dst_address is not None:
                out += ilist(tgt.Store(t0, dst_address))
    return out