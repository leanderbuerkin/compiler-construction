import ast_2_shrunk as src
import ast_3_alloc as tgt
from identifier import Id
from util.immutable_list import *

def alloc(p: src.Program) -> tgt.Program:
    return alloc_stmts(p)

def alloc_stmts(ss: IList[src.Stmt]) -> IList[tgt.Stmt]:
    return IList([alloc_stmt(s) for s in ss])

def alloc_stmt(s: src.Stmt) -> tgt.Stmt:
    match s:
        case src.SExpr(e):
            e_out = alloc_expr(e)
            return tgt.SExpr(e_out)
        case src.SPrint(e):
            e_out = alloc_expr(e)
            return tgt.SPrint(e_out)
        case src.SAssign(x, e):
            e_out = alloc_expr(e)
            return tgt.SAssign(tgt.LId(x), e_out)
        case src.SIf(e, b1, b2):
            e_out = alloc_expr(e)
            b1_out = alloc_stmts(b1)
            b2_out = alloc_stmts(b2)
            return tgt.SIf(e_out, b1_out, b2_out)
        case src.SWhile(e, b):
            e_out = alloc_expr(e)
            b_out = alloc_stmts(b)
            return tgt.SWhile(e_out, b_out)

def alloc_expr(e: src.Expr) -> tgt.Expr:
    match e:
        case src.EConst(c, size):
            return tgt.EConst(c, size)
        case src.EVar(x):
            return tgt.EVar(x)
        case src.EInput():
            return tgt.EInput()
        case src.EOp1(op, e1):
            e1_out = alloc_expr(e1)
            return tgt.EOp1(op, e1_out)
        case src.EOp2(e1, op, e2):
            e1_out = alloc_expr(e1)
            e2_out = alloc_expr(e2)
            return tgt.EOp2(e1_out, op, e2_out)
        case src.EIf(e1, e2, e3):
            e1_out = alloc_expr(e1)
            e2_out = alloc_expr(e2)
            e3_out = alloc_expr(e3)
            return tgt.EIf(e1_out, e2_out, e3_out)
        case src.ETuple(es):
            ...
        case src.ETupleAccess(e, i):
            return tgt.ETupleAccess(alloc_expr(e), i)
        case src.ETupleLen(e):
            return tgt.ETupleLen(alloc_expr(e))

