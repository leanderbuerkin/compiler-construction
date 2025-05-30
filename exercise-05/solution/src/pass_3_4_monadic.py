import ast_3_alloc as src
import ast_4_mon as tgt
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
            p_l, l_out = monadic_lhs(l)
            p_e, e_out = monadic_expr(e)
            return p_l + p_e + ilist(tgt.SAssign(l_out, e_out))
        case src.SIf(e, b1, b2):
            p_e, e_out = monadic_condition(e)
            p1 = monadic_stmts(b1)
            p2 = monadic_stmts(b2)
            return p_e + ilist(tgt.SIf(e_out, p1, p2))
        case src.SWhile(e, b):
            test_body, test_expr = monadic_condition(e)
            loop_body = monadic_stmts(b)
            return ilist(tgt.SWhile(test_body, test_expr, loop_body))
        case src.SCollect(n):
            return ilist(tgt.SCollect(n))

def monadic_lhs(l: src.Lhs) -> tuple[tgt.Program, tgt.Lhs]:
    match l:
        case src.LId(x):
            return ilist(), tgt.LId(x)
        case src.LSubscript(e, i):
            p, a_out = monadic_atom(e)
            return p, tgt.LSubscript(a_out, i)

def monadic_atom(e: src.Expr) -> tuple[IList[tgt.Stmt], tgt.ExprAtom]:
    p, e_out = monadic_expr(e)
    match e_out:
        case tgt.EVar(_) | tgt.EConst(_):
            return p, e_out
        case _:
            x = Id.fresh("x")
            return p + ilist(tgt.SAssign(tgt.LId(x), e_out)), tgt.EVar(x)

def monadic_expr(e: src.Expr) -> tuple[IList[tgt.Stmt], tgt.Expr]:
    match e:
        case src.EConst(c, size):
            return ilist(), tgt.EConst(c, size)
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
            p_e2, e2_out = monadic_expr(e2)
            p_e3, e3_out = monadic_expr(e3)
            x = Id.fresh("x")
            p = p_e1 + ilist(
                tgt.SIf(
                    e1_out,
                    p_e2 + ilist(tgt.SAssign(tgt.LId(x), e2_out)),
                    p_e3 + ilist(tgt.SAssign(tgt.LId(x), e3_out))
                )
            )
            return p, tgt.EVar(x)
        case src.EBegin(body, tail):
            p_body: IList[tgt.Stmt] = ilist()
            for s in body:
                p_body += monadic_stmt(s)
            p_tail, e_tail = monadic_expr(tail)
            return p_body + p_tail, e_tail
        case src.EGlobal(g):
            x = Id.fresh("x")
            p = ilist(tgt.SAssign(tgt.LId(x), tgt.EGlobal(g)))
            return p, tgt.EVar(x)
        case src.EAllocate(n):
            x = Id.fresh("x")
            p = ilist(tgt.SAssign(tgt.LId(x), tgt.EAllocate(n)))
            return p, tgt.EVar(x)
        case src.ETupleAccess(e, i):
            p_e, a_out = monadic_atom(e)
            x = Id.fresh("x")
            p = ilist(tgt.SAssign(tgt.LId(x), tgt.ETupleAccess(a_out, i)))
            return p_e + p, tgt.EVar(x)
        case src.ETupleLen(e):
            p_e, a_out = monadic_atom(e)
            x = Id.fresh("x")
            p = ilist(tgt.SAssign(tgt.LId(x), tgt.ETupleLen(a_out)))
            return p_e + p, tgt.EVar(x)

def monadic_condition(e: src.Expr) -> tuple[IList[tgt.Stmt], tgt.EOp2Comp]:
    match e:
        case src.EOp2(e1, ("==" | "!=" | "<=" | "<" | ">" | ">=") as op, e2):
            p_a1, a1_out = monadic_atom(e1)
            p_a2, a2_out = monadic_atom(e2)
            return (p_a1 + p_a2, tgt.EOp2Comp(a1_out, op, a2_out))
        case src.EOp1("not", e1):
            p_a, a_out = monadic_atom(e1)
            return (p_a, tgt.EOp2Comp(a_out, "==", tgt.EConst(0, '64bit')))
        case _:
            p_a, a_out = monadic_atom(e)
            return (p_a, tgt.EOp2Comp(a_out, "!=", tgt.EConst(0, '64bit')))
