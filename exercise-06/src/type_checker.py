from dataclasses import dataclass
from typing import Optional

from ast_1_python import *
from util.immutable_list import IList
from types_ import *

# Error Type

@dataclass
class TypeError(Exception):
    msg: str

# Typing Context

type TCtx = dict[Id, Type] # Typing context

# Type Checking

def type_check(p: Program):
    ctx: TCtx = dict()

    # Add the types of all declarations to the type context,
    # e.g. `f : Callable[[int], int]` for a function definition.
    for d in p.decls:
        ctx |= decl_binds(d)

    # Check if the declarations are well-typed.
    # As functions may recursively call themselves or other functions,
    # we need their types already in the context.
    # We copy the context, such that local variables from one function
    # don't leak into other functions.
    for d in p.decls:
        type_check_decl(ctx.copy(), d)

    ret_t = type_check_stmts(ctx, p.main_body)
    if ret_t is not None:
        raise TypeError(f"Return statement used outside of any function declaration.")

def decl_binds(d: Decl) -> TCtx:
    match d:
        case DFun(id, params, ret_ty, _):
            param_tys = IList([t for (_, t) in params])
            return { id: TCallable(param_tys, ret_ty) }

def type_check_decl(ctx: TCtx, d: Decl):
    match d:
        case DFun(_, params, ret_ty, body):
            for x, t in params:
                ctx[x] = t
            actual_ret_ty = type_check_stmts(ctx, body)
            if actual_ret_ty is None:
                actual_ret_ty = TNone()
            check_type_equal(ret_ty, actual_ret_ty, d)

def type_check_stmts(ctx: TCtx, ss: IList[Stmt]) -> Optional[Type]:
    ret_ty = None
    for s in ss:
        ret_ty = check_mtype_equal(ret_ty, type_check_stmt(ctx, s), s)
    return ret_ty

def type_check_stmt(ctx: TCtx, s: Stmt) -> Optional[Type]:
    match s:
        case SExpr(e):
            _ = type_check_expr(ctx, e)
            return None
        case SPrint(e):
            te = type_check_expr(ctx, e)
            check_type_equal(te, TInt(), e)
            return None
        case SAssign(x, e):
            te = type_check_expr(ctx, e)
            if x in ctx:
                check_type_equal(te, ctx[x], s)
            else:
                ctx[x] = te
            return None
        case SIf(test, body, orelse):
            ttest = type_check_expr(ctx, test)
            check_type_equal(ttest, TBool(), test)
            ctx_orelse = ctx.copy()
            ret_ty_1 = type_check_stmts(ctx, body)
            ret_ty_2 = type_check_stmts(ctx_orelse, orelse)
            check_ctx_equal(ctx, ctx_orelse, s)
            return check_mtype_equal(ret_ty_1, ret_ty_2, s)
        case SWhile(test, body):
            ttest = type_check_expr(ctx, test)
            check_type_equal(ttest, TBool(), test)
            return type_check_stmts(ctx, body)
        case SReturn(e):
            return type_check_expr(ctx, e)

def type_check_expr(ctx: TCtx, e: Expr) -> Type:
    match e:
        case EConst(x):
            match x:
                case bool(_):
                    return TBool()
                case int(_):
                    if x >= 2 ** 62 or x < -(2 ** 62):
                        raise TypeError(f"Integer constant {x} is too large for 63bit.")
                    else:
                        return TInt()
                case None:
                    return TNone()
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
            if type(t1) is TTuple or type(t2) is TTuple:
                match op:
                    case "is":
                        check_type_equal(t1, t2, e)
                        return TBool()
                    case _:
                        raise TypeError(f"Operator '{op}' is not supported for tuples.")
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
                case "is":
                    raise TypeError("Operator 'is' used on expression of non-tuple type")
        case EInput():
            return TInt()
        case EIf(test, body, orelse):
            ttest = type_check_expr(ctx, test)
            tbody = type_check_expr(ctx, body)
            torelse = type_check_expr(ctx, orelse)
            check_type_equal(ttest, TBool(), test)
            check_type_equal(tbody, torelse, e)
            return tbody
        case ETuple(es):
            return TTuple(IList([type_check_expr(ctx, e) for e in es]))
        case ETupleAccess(e, i):
            t = type_check_expr(ctx, e)
            match t:
                case TTuple(ts):
                    if 0 <= i < len(ts):
                        return ts[i]
                    else:
                        raise TypeError(f"Index {i} is out of bounds for tuple of length {len(ts)}.")
                case t:
                    raise TypeError(f"Tuple access on non-tuple type {t}.")
        case ETupleLen(e):
            t = type_check_expr(ctx, e)
            match t:
                case TTuple(ts):
                    return TInt()
                case t:
                    raise TypeError(f"Tuple length used on non-tuple type {t}.")
        case ECall(func, args):
            t_func = type_check_expr(ctx, func)
            t_args = [type_check_expr(ctx, arg) for arg in args]
            match t_func:
                case TCallable(t_params, t_ret):
                    if len(t_params) != len(t_args):
                        raise TypeError(f"Function call with {len(t_args)} arguments, "
                                        f"but function type {pretty_type(t_func)} with {len(t_params)} parameters")
                    for t_param, t_arg, arg in zip(t_params, t_args, args):
                        check_type_equal(t_param, t_arg, arg)
                    return t_ret
                case _:
                    raise TypeError(f"Function call on expression of non-functino type. "
                                    f"Expression: {pretty_expr(func)}, "
                                    f"Type: {pretty_type(t_func)}")

# Type Equality

def check_type_equal(thave: Type, texpect: Type, es: Expr | Stmt | Decl):
    if thave != texpect:
        raise TypeError(f"I got '{pretty_type(thave)}' but I expected '{pretty_type(texpect)}' in '{pretty_anything(es)}'")

def check_ctx_equal(ctx1: TCtx, ctx2: TCtx, es: Expr | Stmt):
    for x in ctx1:
        if x in ctx2:
            check_type_equal(ctx1[x], ctx2[x], es)
        else:
            del ctx1[x]

def check_mtype_equal(t1: Optional[Type], t2: Optional[Type], esd: Expr | Stmt | Decl) -> Optional[Type]:
        match t1, t2:
            case None, t:
                return t
            case t, None:
                return t
            case t1, t2:
                check_type_equal(t1, t2, esd)
                return t1

# Pretty Printing

def pretty_type(t: Type) -> str:
    match t:
        case TBool():
            return "bool"
        case TInt():
            return "int"
        case TTuple(ts):
            return "tuple[" + ", ".join(pretty_type(t) for t in ts) + "]"
        case TCallable(params_tys, ret_ty):
            return "Callable[[" + ", ".join(pretty_type(t) for t in params_tys) + f"], {pretty_type(ret_ty)}]"
        case TNone():
            return "None"