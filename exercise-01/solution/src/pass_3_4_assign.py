import ast_3_sel as src
import ast_4_mem as tgt
from identifier import Id
from register import *
from util.immutable_list import ilist

def assign_homes(p: src.Program) ->  tuple[tgt.Program, int]:
    p_out: tgt.Program = ilist()
    env: dict[Id, int] = dict()
    for i in p:
        p_out += ilist(assign_homes_instr(env, i))
    return p_out, (len(env) + 2) * 8

def assign_homes_instr(env: dict[Id, int], i: src.Instr) -> tgt.Instr:
    match i:
        case src.Move(dst, src_):
            return tgt.Move(assign_home_dst(env, dst), assign_home_src(env, src_))
        case src.Call(src_):
            return tgt.Call(src_)
        case src.Instr2(op, dst, src1, src2):
            return tgt.Instr2(
                op,
                assign_home_dst(env, dst),
                assign_home_src(env, src1),
                assign_home_src(env, src2),
            )

def assign_home_dst(env: dict[Id, int], arg: src.ArgWrite) -> tgt.ArgWrite:
    match arg:
        case Id(_) as x:
            return assign_home_id(env, x)
        case Register(r):
            return Register(r)

def assign_home_src(env: dict[Id, int], arg: src.ArgRead) -> tgt.ArgRead:
    match arg:
        case src.Const(i):
            return tgt.Const(i)
        case _:
            return assign_home_dst(env, arg)

def assign_home_id(env: dict[Id, int], x: Id) -> tgt.Offset:
    if x not in env:
        env[x] = (len(env) + 3) * 8
    return tgt.Offset(fp, -env[x])
