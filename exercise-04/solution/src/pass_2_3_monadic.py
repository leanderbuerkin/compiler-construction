import ast_2_shrunk as src
import ast_3_mon as tgt
from identifier import Id
from util.immutable_list import IList, ilist

def monadic(p: src.Program) -> tgt.Program:
    return monadic_stmts(p)

def monadic_stmts(ss: IList[src.Stmt]) -> IList[tgt.Stmt]:
    out: IList[tgt.Stmt] = ilist()
    for s in ss:
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
        case src.SIf(e, b1, b2):
            p_e, e_out = monadic_condition(e)
            p1 = monadic_stmts(b1)
            p2 = monadic_stmts(b2)
            return p_e + ilist(tgt.SIf(e_out, p1, p2))
        case src.SWhile(e, b):
            test_body, test_expr = monadic_condition(e)
            loop_body = monadic_stmts(b)
            return ilist(tgt.SWhile(test_body, test_expr, loop_body))

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
            match op:
                case "+" | "-":
                   return p_a1 + p_a2,  tgt.EOp2Arith(a1_out, op, a2_out)
                case "==" | "!=" | "<=" | "<" | ">" | ">=":
                   return p_a1 + p_a2, tgt.EOp2Comp(a1_out, op, a2_out)
        case src.EIf(e1, e2, e3):
            p_e1, e1_out = monadic_condition(e1)
            p_a2, a2_out = monadic_atom(e2)
            p_a3, a3_out = monadic_atom(e3)
            x = Id.fresh("x")
            p = p_e1 + ilist(
                tgt.SIf(
                    e1_out,
                    p_a2 + ilist(tgt.SAssign(x, a2_out)),
                    p_a3 + ilist(tgt.SAssign(x, a3_out))
                )
            )
            return p, tgt.EVar(x)

def monadic_condition(e: src.Expr) -> tuple[IList[tgt.Stmt], tgt.EOp2Comp]:
    match e:
        case src.EOp2(e1, ("==" | "!=" | "<=" | "<" | ">" | ">=") as op, e2):
            p_a1, a1_out = monadic_atom(e1)
            p_a2, a2_out = monadic_atom(e2)
            return (p_a1 + p_a2, tgt.EOp2Comp(a1_out, op, a2_out))
        case src.EOp1("not", e1):
            p_a, a_out = monadic_atom(e1)
            return (p_a, tgt.EOp2Comp(a_out, "==", tgt.EConst(False)))
        case _:
            p_a, a_out = monadic_atom(e)
            return (p_a, tgt.EOp2Comp(a_out, "!=", tgt.EConst(False)))
