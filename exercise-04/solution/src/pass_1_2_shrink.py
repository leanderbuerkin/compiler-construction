import ast_1_python as src
import ast_2_shrunk as tgt
from types_ import *
from identifier import *
from util.immutable_list import *

def shrink(p: src.Program) -> tgt.Program:
    return shrink_stmts(p)

def shrink_stmts(ss: IList[src.Stmt]) -> IList[tgt.Stmt]:
    return IList([shrink_stmt(s) for s in ss])

def shrink_stmt(s: src.Stmt) -> tgt.Stmt:
    match s:
        case src.SExpr(e):
            e_out = shrink_expr(e)
            return tgt.SExpr(e_out)
        case src.SPrint(e):
            e_out = shrink_expr(e)
            return tgt.SPrint(e_out)
        case src.SAssign(x, e):
            e_out= shrink_expr(e)
            return tgt.SAssign(x, e_out)
        case src.SIf(e, b1, b2):
            e_out = shrink_expr(e)
            b1_out = shrink_stmts(b1)
            b2_out = shrink_stmts(b2)
            return tgt.SIf(e_out, b1_out, b2_out)
        case src.SWhile(e, b):
            e_out = shrink_expr(e)
            b_out = shrink_stmts(b)
            return tgt.SWhile(e_out, b_out)

def shrink_expr(e: src.Expr) -> tgt.Expr:
    match e:
        case src.EConst(c):
            return tgt.EConst(c)
        case src.EVar(x):
            return tgt.EVar(x)
        case src.EInput():
            return tgt.EInput()
        case src.EOp1(op, e):
            e_out = shrink_expr(e)
            return tgt.EOp1(op, e_out)
        case src.EOp2(e1, op, e2):
            e1_out = shrink_expr(e1)
            e2_out = shrink_expr(e2)
            match op:
                case "and":
                    return tgt.EIf(e1_out, e2_out, tgt.EConst(False))
                case "or":
                    return tgt.EIf(e1_out, tgt.EConst(True), e2_out)
                case _:
                    return tgt.EOp2(e1_out, op, e2_out)
        case src.EIf(e1, e2, e3):
            e1_out = shrink_expr(e1)
            e2_out = shrink_expr(e2)
            e3_out = shrink_expr(e3)
            return tgt.EIf(e1_out, e2_out, e3_out)