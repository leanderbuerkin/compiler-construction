import ast_4_exp as src
import ast_5_sel as tgt
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
                tgt.Call(Label("print_int64"), 1),
            )
        case src.SAssign(x, src.EConst(n)):
            return ilist(tgt.Move(x, tgt.Const(int(n))))
        case src.SAssign(x, src.EVar(y)):
            return ilist(tgt.Move(x, y))
        case src.SAssign(x, src.EInput()):
            return ilist(
                tgt.Call(Label("input_int64"), 0),
                tgt.Move(x, a0),
            )
        case src.SAssign(lhs, src.EOp1(op, e)):
            match op:
                case "not":
                    return ilist(
                        tgt.Instr2("sub", lhs, tgt.Const(2), select_atom(e))
                    )
                case "-":
                    return ilist(
                        tgt.Instr2("sub", lhs, tgt.Const(0), select_atom(e))
                    )
        case src.SAssign(lhs, src.EOp2Arith(e1, op, e2)):
            match op:
                case "+":
                    return ilist(
                        tgt.Instr2("add", lhs, select_atom(e1), select_atom(e2))
                    )
                case "-":
                    return ilist(
                        tgt.Instr2("sub", lhs, select_atom(e1), select_atom(e2))
                    )
        case src.SAssign(lhs, src.EOp2Comp(e1, op, e2)):
            match op:
                case "==":
                    return ilist(
                        tgt.Instr2("sub", lhs, select_atom(e1), select_atom(e2)),
                        tgt.Instr2("sltu", lhs, lhs, tgt.Const(1))
                    )
                case "!=":
                    return ilist(
                        tgt.Instr2("sub", lhs, select_atom(e1), select_atom(e2)),
                        tgt.Instr2("sltu", lhs, zero, lhs),
                    )
                case "<":
                    return ilist(
                        tgt.Instr2("slt", lhs, select_atom(e1), select_atom(e2)),
                    )
                case ">":
                    return ilist(
                        tgt.Instr2("slt", lhs, select_atom(e2), select_atom(e1)),
                    )
                case "<=":
                    return ilist(
                        tgt.Instr2("slt", lhs, select_atom(e2), select_atom(e1)),
                        tgt.Instr2("xor", lhs, lhs, tgt.Const(1)),
                    )
                case ">=":
                    return ilist(
                        tgt.Instr2("slt", lhs, select_atom(e1), select_atom(e2)),
                        tgt.Instr2("xor", lhs, lhs, tgt.Const(1)),
                    )
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

def select_atom(e: src.ExprAtom) -> tgt.Const | Id:
    match e:
        case src.EConst(c):
            return tgt.Const(int(c))
        case src.EVar(x):
            return x
