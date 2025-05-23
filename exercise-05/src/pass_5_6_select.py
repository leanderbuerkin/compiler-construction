import ast_5_exp as src
import ast_6_sel as tgt
from identifier import Id
from label import Label
from register import *
from util.immutable_list import ilist, IList

def select(p: src.Program) -> tgt.Program:
    out: tgt.Program = dict()
    for label in p:
        out[label] = select_block(p[label])
    return out

def select_block (p: src.Block) -> tgt.Block:
    out: tgt.Block = ilist()
    for s in p:
        out += select_stmt(s)
    return out

def select_stmt(s: src.Stmt) -> IList[tgt.Instr]:
    match s:
        case src.SPrint(e):
            return ilist(
                tgt.Move(a0, select_atom(e)),
                # TODO
                tgt.Call(Label("print_int64"), 1),
            )
        case src.SAssign(lhs, src.EConst(n, size)):
            return ilist(tgt.Move(select_lhs(lhs), tgt.Const(int(n), size)))
        case src.SAssign(lhs, src.EVar(y)):
            return ilist(tgt.Move(select_lhs(lhs), y))
        case src.SAssign(lhs, src.EInput()):
            return ilist(
                tgt.Call(Label("input_int64"), 0),
                # TODO
                tgt.Move(select_lhs(lhs), a0),
            )
        case src.SAssign(lhs, src.EOp1(op, e)):
            match op:
                case "not":
                    return ilist(
                         # TODO
                    )
                case "-":
                    return ilist(
                        tgt.Instr2("sub", select_lhs(lhs), tgt.Const(0, "64bit"), select_atom(e))
                    )
        case src.SAssign(lhs, src.EOp2Arith(e1, op, e2)):
            match op:
                case "+":
                    return ilist(
                        tgt.Instr2("add", select_lhs(lhs), select_atom(e1), select_atom(e2))
                    )
                case "-":
                    return ilist(
                        tgt.Instr2("sub", select_lhs(lhs), select_atom(e1), select_atom(e2))
                    )
        case src.SAssign(lhs, src.EOp2Comp(e1, op, e2)):
            lhs_out = select_lhs(lhs)
            match op:
                case "==":
                    return ilist(
                        tgt.Instr2("sub", lhs_out, select_atom(e1), select_atom(e2)),
                        tgt.Instr2("sltu", lhs_out, lhs_out, tgt.Const(1, "64bit")),
                        # TODO
                    )
                case "!=":
                    return ilist(
                        tgt.Instr2("sub", lhs_out, select_atom(e1), select_atom(e2)),
                        tgt.Instr2("sltu", lhs_out, zero, lhs_out),
                        # TODO
                    )
                case "<":
                    return ilist(
                        tgt.Instr2("slt", lhs_out, select_atom(e1), select_atom(e2)),
                        # TODO
                    )
                case ">":
                    return ilist(
                        tgt.Instr2("slt", lhs_out, select_atom(e2), select_atom(e1)),
                        # TODO
                    )
                case "<=":
                    return ilist(
                        tgt.Instr2("slt", lhs_out, select_atom(e2), select_atom(e1)),
                        tgt.Instr2("xor", lhs_out, lhs_out, tgt.Const(1, "64bit")),
                        # TODO
                    )
                case ">=":
                    return ilist(
                        tgt.Instr2("slt", lhs_out, select_atom(e1), select_atom(e2)),
                        tgt.Instr2("xor", lhs_out, lhs_out, tgt.Const(1, "64bit")),
                        # TODO
                    )
        case src.SAssign(lhs, src.EAllocate(num_elems)):
            ...
        case src.SAssign(lhs, src.ETupleLen(e)):
            ...
        case src.SAssign(lhs, src.ETupleAccess(e, i)):
            lhs_out = select_lhs(lhs)
            match select_atom(e):
                case tgt.Const(_, _):
                    raise Exception("Subscripting on a constant is forbidden")
                case tgt.Id(_) as x:
                    ...
        case src.SAssign(lhs, src.EGlobal(g)):
            ...
        case src.SCollect(num_words):
           ...
        case src.SIf(src.EOp2Comp(e1, op, e2), body_label, orelse_label):
            match op:
                case "==":
                    cc: tgt.BranchName = "beq"
                case "!=":
                    cc = "bne"
                case "<":
                    cc = "blt"
                case "<=":
                    cc = "bge"
                    e2, e1 = e1, e2
                case ">":
                    cc = "blt"
                    e2, e1 = e1, e2
                case ">=":
                    cc = "bge"
            return ilist(
                tgt.Branch(cc, select_atom(e1), select_atom(e2), body_label),
                tgt.Jump(orelse_label),
            )
        case src.SGoto(target):
            return ilist(tgt.Jump(target))
        case _:
            raise Exception(f"Impossible statement {s}!")

def select_lhs(lhs: src.Lhs) -> Id | tgt.Offset:
    match lhs:
        case src.LId(x):
            return x
        case src.LSubscript(e, i):
            match select_atom(e):
                case tgt.Const(_, _):
                    raise Exception("Subscripting on a constant is forbidden")
                case Id(_) as x:
                    ...

def select_atom(e: src.ExprAtom) -> tgt.Const | Id:
    match e:
        case src.EConst(c, size):
            return tgt.Const(int(c), size)
        case src.EVar(x):
            return x
