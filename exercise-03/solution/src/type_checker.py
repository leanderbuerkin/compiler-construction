from dataclasses import dataclass

from ast_1_python import *
from types_ import *
from util.immutable_list import IList
from identifier import Id

# Error Type
@dataclass
class TypeError(Exception):
    msg: str

# Typing context
type TCtx = dict[Id, Type]

# Type Checking
def type_check(p: Program) -> None:
    ctx: TCtx = dict()
    type_check_stmts(ctx, p)

def type_check_stmts(ctx: TCtx, ss: IList[Stmt]) -> None:
    for s in ss:
        type_check_stmt(ctx, s)

def type_check_stmt(ctx: TCtx, s: Stmt) -> None:
    match s:
        case SExpr(e):
            _ = type_check_expr(ctx, e)
        case SPrint(e):
            te = type_check_expr(ctx, e)
            check_type_equal(te, TInt(), e)
        case SAssign(x, e):
            te = type_check_expr(ctx, e)
            if x in ctx:
                check_type_equal(te, ctx[x], s)
            else:
                ctx[x] = te
        case SIf(test, body, orelse):
            ttest = type_check_expr(ctx, test)
            check_type_equal(ttest, TBool(), test)
            ctx_orelse = ctx.copy()
            type_check_stmts(ctx, body)
            type_check_stmts(ctx_orelse, orelse)
            check_ctx_equal(ctx, ctx_orelse, s)

# infer type of an expression
def type_check_expr(ctx: TCtx, e: Expr) -> Type:
    match e:
        case EConst(x):
            match x:
                case bool(_):
                    return TBool()
                case int(_):
                    if x >= 2**63 or x < -(2**63):
                        raise TypeError(f"Integer constant {x} is too large for 64bit.")
                    else:
                        return TInt()
        case EVar(x):
            if x in ctx:
                return ctx[x]
            else:
                raise TypeError(f"Undefined variable {x}.")
        case EOp1(op, e):
            te = type_check_expr(ctx, e)
            match op:
                case "-":
                    check_type_equal(te, TInt(), e)
                    return TInt()
                case "not":
                    check_type_equal(te, TBool(), e)
                    return TBool()
        case EOp2(e1, op, e2):
            t1 = type_check_expr(ctx, e1)
            t2 = type_check_expr(ctx, e2)
            match op:
                case "+" | "-":
                    check_type_equal(t1, TInt(), e1)
                    check_type_equal(t2, TInt(), e2)
                    return TInt()
                case "==" | "!=":
                    check_type_equal(t1, t2, e)
                    return TBool()
                case "<=" | "<" | ">" | ">=":
                    check_type_equal(t1, TInt(), e1)
                    check_type_equal(t2, TInt(), e2)
                    return TBool()
                case "and" | "or":
                    check_type_equal(t1, TBool(), e1)
                    check_type_equal(t2, TBool(), e2)
                    return TBool()
        case EInput():
            return TInt()
        case EIf(test, body, orelse):
            ttest = type_check_expr(ctx, test)
            tbody = type_check_expr(ctx, body)
            torelse = type_check_expr(ctx, orelse)
            check_type_equal(ttest, TBool(), test)
            check_type_equal(tbody, torelse, e)
            return tbody

# check expression against given type
def check_expr(ctx: TCtx, e: Expr, ty: Type) -> None:
    match e:
        case _:
            te = type_check_expr(ctx, e)
            check_type_equal(te, ty, e)

# Type Equality
def check_type_equal(thave: Type, texpect: Type, es: Expr | Stmt) -> None:
    if thave != texpect:
        raise TypeError(f"I got {repr(thave)} but I expected {repr(texpect)} in {repr(es)}")

def check_ctx_equal(ctx1: TCtx, ctx2: TCtx, es: Expr | Stmt) -> None:
    for x in ctx1:
        if x in ctx2:
            check_type_equal(ctx1[x], ctx2[x], es)
        else:
            del ctx1[x]
