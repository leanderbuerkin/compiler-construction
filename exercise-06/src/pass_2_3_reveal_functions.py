# The only interesting thing happens in `collect_function_arities` and
# the variable case of `reveal_expr`.

import ast_2_shrunk as src
import ast_3_revealed as tgt
from identifier import Id
from util.immutable_list import *

# BEGIN
def reveal(p: src.Program) -> tgt.Program:
    arities = collect_function_arities(p)
    return IList([reveal_decl(arities, d) for d in p])

def collect_function_arities(p: src.Program) -> dict[Id, int]:
    arities = {}
    for d in p:
        match d:
            case src.DFun(name, params, _, _):
                arities[name] = len(params)
    return arities

def reveal_decl(arities: dict[Id, int], d: src.Decl) -> tgt.Decl:
    match d:
        case src.DFun(name, params, ret_ty, body):
            return tgt.DFun(name, params, ret_ty, reveal_stmts(arities, body))

def reveal_stmts(arities: dict[Id, int], ss: IList[src.Stmt]) -> IList[tgt.Stmt]:
    return IList([reveal_stmt(arities, s) for s in ss])

def reveal_stmt(arities: dict[Id, int], s: src.Stmt) -> tgt.Stmt:
    match s:
        case src.SExpr(e):
            e_out = reveal_expr(arities, e)
            return tgt.SExpr(e_out)
        case src.SPrint(e):
            e_out = reveal_expr(arities, e)
            return tgt.SPrint(e_out)
        case src.SAssign(x, e):
            e_out = reveal_expr(arities, e)
            return tgt.SAssign(x, e_out)
        case src.SIf(e, b1, b2):
            e_out = reveal_expr(arities, e)
            b1_out = reveal_stmts(arities, b1)
            b2_out = reveal_stmts(arities, b2)
            return tgt.SIf(e_out, b1_out, b2_out)
        case src.SWhile(e, b):
            e_out = reveal_expr(arities, e)
            b_out = reveal_stmts(arities, b)
            return tgt.SWhile(e_out, b_out)
        case src.SReturn(e):
            e_out = reveal_expr(arities, e)
            return tgt.SReturn(e_out)

def reveal_expr(arities: dict[Id, int], e: src.Expr) -> tgt.Expr:
    match e:
        case src.EConst(c, size):
            return tgt.EConst(c, size)
        case src.EVar(x):
            ...
        case src.EInput():
            return tgt.EInput()
        case src.EOp1(op, e1):
            e1_out = reveal_expr(arities, e1)
            return tgt.EOp1(op, e1_out)
        case src.EOp2(e1, op, e2):
            e1_out = reveal_expr(arities, e1)
            e2_out = reveal_expr(arities, e2)
            return tgt.EOp2(e1_out, op, e2_out)
        case src.EIf(e1, e2, e3):
            e1_out = reveal_expr(arities, e1)
            e2_out = reveal_expr(arities, e2)
            e3_out = reveal_expr(arities, e3)
            return tgt.EIf(e1_out, e2_out, e3_out)
        case src.ETupleAccess(e, i):
            return tgt.ETupleAccess(reveal_expr(arities, e), i)
        case src.ETupleLen(e):
            return tgt.ETupleLen(reveal_expr(arities, e))
        case src.ETuple(es):
            return tgt.ETuple(reveal_exprs(arities, es))
        case src.ECall(e_func, e_args):
            return tgt.ECall(reveal_expr(arities, e_func), reveal_exprs(arities, e_args))

def reveal_exprs(arities: dict[Id, int], es: IList[src.Expr]) -> IList[tgt.Expr]:
    return IList([reveal_expr(arities, e) for e in es])
# END

