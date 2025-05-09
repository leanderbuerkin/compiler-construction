import ast_1_python as src
import ast_2_mon as tgt
from identifier import Id
from util.immutable_list import IList, ilist

def monadic(p: src.Program) -> tgt.Program:
    out: IList[tgt.Stmt] = ilist()
    for s in p:
        out += monadic_stmt(s)
    return out

def monadic_stmt(s: src.Stmt) -> IList[tgt.Stmt]:
    match s:
        case src.SExpr(e):
            p_a, a_out = monadic_atom(e)
            return p_a
        case src.SPrint(e):
            p_a, a_out = monadic_atom(e)
            return p_a + ilist(tgt.SPrint(a_out))
        case src.SAssign(l, e):
            p_e, e_out = monadic_expr(e)
            return  p_e + ilist(tgt.SAssign(l, e_out))

def monadic_atom(e: src.Expr) -> tuple[IList[tgt.Stmt], tgt.ExprAtom]:
    p, e_out = monadic_expr(e)
    match e_out:
        case tgt.EVar(_) | tgt.EConst(_):
            return p, e_out
        case _:
            x = Id.fresh("x")
            return p + ilist(tgt.SAssign(x, e_out)), tgt.EVar(x)

def monadic_expr(e: src.Expr) -> tuple[IList[tgt.Stmt], tgt.Expr]:
    match e:
        case src.EConst(c):
            return ilist(), tgt.EConst(c)
        case src.EVar(x):
            return ilist(), tgt.EVar(x)
        case src.EOp1(op, e):
            p_a, a_out = monadic_atom(e)
            return p_a, tgt.EOp1(op, a_out)
        case src.EInput():
            return ilist(), tgt.EInput()
        case src.EOp2(e1, op, e2):
            p_a1, a1_out = monadic_atom(e1)
            p_a2, a2_out = monadic_atom(e2)
            return p_a1 + p_a2, tgt.EOp2Arith(a1_out, op, a2_out)
