import ast_1_python as src
import ast_2_shrunk as tgt
from types_ import *
from util.immutable_list import *

def shrink(p: src.Program) -> tgt.Program:
    new_decls = IList([shrink_decl(d) for d in p.decls])
    main_body = shrink_stmts(p.main_body)
    main = tgt.DFun(tgt.Id("main"), ilist(), main_body)
    return new_decls + ilist(main)

def shrink_decl(d: src.Decl) -> tgt.Decl:
    match d:
        case src.DFun(name, params, _, body):
            params = IList([x for (x, _) in params])
            return tgt.DFun(name, params, shrink_stmts(body))

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
        # BEGIN
        case src.SAssign(x, _, e):
        # END
            e_out = shrink_expr(e)
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
        case src.SReturn(e):
            e_out = shrink_expr(e)
            return tgt.SReturn(e_out)

def shrink_expr(e: src.Expr) -> tgt.Expr:
    match e:
        case src.EConst(c):
            return tgt.EConst(c, '63bit')
        case src.EVar(x):
            return tgt.EVar(x)
        case src.EInput():
            return tgt.EInput()
        case src.EOp1(op, e1):
            e1 = shrink_expr(e1)
            return tgt.EOp1(op, e1)
        case src.EOp2(e1, op, e2):
            e1 = shrink_expr(e1)
            e2 = shrink_expr(e2)
            match op:
                case "and":
                    return tgt.EIf(e1, e2, tgt.EConst(False, '63bit'))
                case "or":
                    return tgt.EIf(e1, tgt.EConst(True, '63bit'), e2)
                case "is":
                    # As tuples are represented as pointers, the 'is' operator
                    # corresponds simply to equality.
                    return tgt.EOp2(e1, "==", e2)
                case _:
                    return tgt.EOp2(e1, op, e2)
        case src.EIf(e1, e2, e3):
            e1 = shrink_expr(e1)
            e2 = shrink_expr(e2)
            e3 = shrink_expr(e3)
            return tgt.EIf(e1, e2, e3)
        case src.ETuple(es):
            return tgt.ETuple(IList([shrink_expr(e) for e in es]))
        case src.ETupleAccess(e, i):
            return tgt.ETupleAccess(shrink_expr(e), i)
        case src.ETupleLen(e):
            return tgt.ETupleLen(shrink_expr(e))
        case src.ECall(e_fun, e_args):
            e_fun = shrink_expr(e_fun)
            e_args = IList([shrink_expr(arg) for arg in e_args])
            return tgt.ECall(e_fun, e_args)
        # BEGIN
        case src.ELambda(params, body):
            return tgt.ELambda(params, shrink_expr(body))
        # END
