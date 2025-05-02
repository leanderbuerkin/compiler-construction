import ast_2_mon as src
import ast_3_sel as tgt
from identifier import Id
from label import Label
from register import *
from util.immutable_list import ilist, IList

def select(p: src.Program) -> tgt.Program:
    out: IList[tgt.Instr] = ilist()
    for s in p:
        out += select_stmt(s)
    return out

def select_stmt(s: src.Stmt) -> IList[tgt.Instr]:
    match s:
        case src.SPrint(e):
            return ilist(
                tgt.Move(a0, select_atom(e)),
                tgt.Call(Label("print_int64")),
            )
        case src.SAssign(x, src.EOp2Arith(e1, "+", e2)):
            return ilist(tgt.Instr2("add", x, select_atom(e1), select_atom(e2)))
        case src.SAssign(x, src.EOp2Arith(e1, "-", e2)):
            return ilist(tgt.Instr2("sub", x, select_atom(e1), select_atom(e2)))
        case src.SAssign(x, src.EOp1("-", e)):
            return ilist(tgt.Instr2("sub", x, tgt.Const(0), select_atom(e)))
        case src.SAssign(x, src.EConst(n)):
            return ilist(tgt.Move(x, tgt.Const(n)))
        case src.SAssign(x, src.EVar(y)):
            return ilist(tgt.Move(x, y))
        case src.SAssign(x, src.EInput()):
            return ilist(
                tgt.Call(Label("input_int64")),
                tgt.Move(x, a0),
            )
        case _:
            raise Exception("Impossible!")

def select_atom(e: src.ExprAtom) -> tgt.Const | Id:
    match e:
        case src.EConst(c):
            return tgt.Const(c)
        case src.EVar(x):
            return x
