import ast_5_sel as src
import ast_6_mem as tgt
from identifier import Id
from register import *
from util.immutable_list import ilist

from register_allocation import RegAllocOutput

def assign_homes(p: src.Program, reg_alloc: RegAllocOutput) -> tgt.Program:
    out: tgt.Blocks = {}
    for label, block in p.items():
        block_out: tgt.Block = ilist()
        for i in block:
            block_out += ilist(assign_homes_instr(reg_alloc.env, i))
        out[label] = block_out
    return out

def assign_homes_instr(env: dict[Id, Register | tgt.Offset], i: src.Instr) -> tgt.Instr:
    match i:
        case src.Move(dst, src_):
            return tgt.Move(assign_home_dst(env, dst), assign_home_src(env, src_))
        case src.Call(src_, _):
            return tgt.Call(src_)
        case src.Jump(label):
            return tgt.Jump(label)
        case src.Branch(cc, rs1, rs2, target):
            return tgt.Branch(cc, assign_home_src(env, rs1), assign_home_src(env, rs2), target)
        case src.Instr2(op, dst, src1, src2):
            return tgt.Instr2(
                op,
                assign_home_dst(env, dst),
                assign_home_src(env, src1),
                assign_home_src(env, src2),
            )

def assign_home_dst(env: dict[Id, Register | tgt.Offset], arg: src.ArgWrite) -> tgt.ArgWrite:
    match arg:
        case Id(_) as x:
            return assign_home_id(env, x)
        case Register(r):
            return Register(r)

def assign_home_src(env: dict[Id, Register | tgt.Offset], arg: src.ArgRead) -> tgt.ArgRead:
    match arg:
        case src.Const(i):
            return tgt.Const(i)
        case _:
            return assign_home_dst(env, arg)

def assign_home_id(env: dict[Id, Register | tgt.Offset], x: Id) -> Register | tgt.Offset:
    if x not in env:
        raise Exception(
            f"Expected {x} to have either a register or stack location assigned!"
        )
    return env[x]
