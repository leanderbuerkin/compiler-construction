# The interesting parts happen at function declarations and function calls

import ast_3_revealed as src
import ast_3_revealed as tgt
from identifier import Id
from types_ import *
from util.immutable_list import *

def limit(p: src.Program) -> tgt.Program:
    return IList([limit_decl(d) for d in p])

def limit_decl(d: src.Decl) -> tgt.Decl:
    match d:
        case src.DFun(name, params, ret_ty, body):
            ...

def limit_stmts(ss: IList[src.Stmt]) -> IList[tgt.Stmt]:
    return IList([limit_stmt(s) for s in ss])

def limit_stmt(s: src.Stmt) -> tgt.Stmt:
    match s:
        case src.SExpr(e):
            e_out = limit_expr(e)
            return tgt.SExpr(e_out)
        case src.SPrint(e):
            e_out = limit_expr(e)
            return tgt.SPrint(e_out)
        case src.SAssign(x, e):
            e_out = limit_expr(e)
            return tgt.SAssign(x, e_out)
        case src.SIf(e, b1, b2):
            e_out = limit_expr(e)
            b1_out = limit_stmts(b1)
            b2_out = limit_stmts(b2)
            return tgt.SIf(e_out, b1_out, b2_out)
        case src.SWhile(e, b):
            e_out = limit_expr(e)
            b_out = limit_stmts(b)
            return tgt.SWhile(e_out, b_out)
        case src.SReturn(e):
            e_out = limit_expr(e)
            return tgt.SReturn(e_out)

def limit_expr(e: src.Expr) -> tgt.Expr:
    match e:
        case src.EConst(c, size):
            return tgt.EConst(c, size)
        case src.EVar(x):
            return tgt.EVar(x)
        case src.EInput():
            return tgt.EInput()
        case src.EOp1(op, e1):
            e1_out = limit_expr(e1)
            return tgt.EOp1(op, e1_out)
        case src.EOp2(e1, op, e2):
            e1_out = limit_expr(e1)
            e2_out = limit_expr(e2)
            return tgt.EOp2(e1_out, op, e2_out)
        case src.EIf(e1, e2, e3):
            e1_out = limit_expr(e1)
            e2_out = limit_expr(e2)
            e3_out = limit_expr(e3)
            return tgt.EIf(e1_out, e2_out, e3_out)
        case src.ETuple(es):
            return tgt.ETuple(limit_exprs(es))
        case src.ETupleAccess(e, i):
            return tgt.ETupleAccess(limit_expr(e), i)
        case src.ETupleLen(e):
            return tgt.ETupleLen(limit_expr(e))
        case src.ECall(e_func, e_args):
            ...
        case src.EFunRef(name, num_params):
            return tgt.EFunRef(name, num_params)

def limit_exprs(es: IList[src.Expr]) -> IList[tgt.Expr]:
    return IList([limit_expr(e) for e in es])

