from dataclasses import dataclass
from typing import Optional

from ast_1_python import *

# Simulate Integer Overflow Behavior

MAX_INT_63 = 2**62 - 1
MIN_INT_63 = -(2**62)

def simulate_over_and_underflow(i: int) -> int:
    while i > MAX_INT_63:
        i = i - (2**63)
    while i < MIN_INT_63:
        i = i + (2**63)
    return i

# Values

type Value = int | bool | VTuple | VNone | VFun

@dataclass(frozen=True)
class VTuple:
    entries: list[Value]

@dataclass(frozen=True)
class VNone:
    pass

@dataclass(frozen=True)
class VFun:
    params: IList[Id]
    body: IList[Stmt]
    env: 'RTEnv'

# Value Environment

type RTEnv = dict[Id, Value]

# Evaluation

def eval_expr(env: RTEnv, e: Expr) -> Value:
    match e:
        case EConst(c):
            if c is None:
                return VNone()
            return c
        case EVar(x):
            return env[x]
        case EOp1(op, e):
            v = eval_expr(env, e)
            match v:
                case VTuple(_):
                    raise Exception(f"Unary operator '{op}' not allowed on tuples.")
                case VNone():
                    raise Exception(f"Unary operator '{op}' not allowed on None.")
                case VFun(_, _, _):
                    raise Exception(f"Unary operator '{op}' not allowed on functions.")
                case _:
                    match op:
                        case "-":
                            return -v
                        case "not":
                            return not v
        case EOp2(e1, "and", e2):
            v1 = eval_expr(env, e1)
            if v1:
                return eval_expr(env, e2)
            return False
        case EOp2(e1, "or", e2):
            v1 = eval_expr(env, e1)
            if not v1:
                return eval_expr(env, e2)
            return True
        case EOp2(e1, op, e2):
            v1 = eval_expr(env, e1)
            v2 = eval_expr(env, e2)
            match v1, v2:
                case (int(x1) | bool(x1)), (int(x2) | bool(x2)):
                    match op:
                        case "+":
                            return simulate_over_and_underflow(x1 + x2)
                        case "-":
                            return simulate_over_and_underflow(x1 - x2)
                        case "==":
                            return x1 == x2
                        case "!=":
                            return x1 != x2
                        case "<=":
                            return x1 <= x2
                        case "<":
                            return x1 < x2
                        case ">":
                            return x1 > x2
                        case ">=":
                            return x1 >= x2
                        case _:
                            raise Exception("Impossible!")
                case VTuple(_), VTuple(_):
                    match op:
                        case "is":
                            return v1 is v2
                        case _:
                            raise Exception("Impossible!")
                case _:
                    raise Exception("Binary operator not allowed on these operands.")
        case EIf(test, body, orelse):
            v1 = eval_expr(env, test)
            if v1:
                return eval_expr(env, body)
            else:
                return eval_expr(env, orelse)
        case EInput():
            while True:
                try:
                    res = int(input())
                    return simulate_over_and_underflow(res)
                except ValueError:
                    continue
        case ETuple(es):
            return VTuple([eval_expr(env, e) for e in es])
        case ETupleAccess(e, i):
            match eval_expr(env, e):
                case VTuple(vs):
                    return vs[i]
                case _:
                    raise Exception("Tried to index into a non-tuple value.")
        case ETupleLen(e):
            match eval_expr(env, e):
                case VTuple(vs):
                    return len(vs)
                case _:
                    raise Exception("Tried to get length of non-tuple value.")
        case ECall(e_func, e_args):
            v_func = eval_expr(env, e_func)
            v_args = [ eval_expr(env, arg) for arg in e_args ]
            match v_func:
                case VFun(params, body, env):
                    call_env = env.copy()
                    for param, v_arg in zip(params, v_args):
                        call_env[param] = v_arg
                    v_ret = eval_stmts(call_env, body)
                    if v_ret is None:
                        return VNone()
                    else:
                        return v_ret
                case _:
                    raise Exception("Tried to call a non-function value.")
        case _:
            raise Exception("Impossible!")

def eval_stmt(env: RTEnv, s: Stmt) -> Optional[Value]:
    match s:
        case SExpr(e):
            eval_expr(env, e)
            return None
        case SPrint(e):
            print(eval_expr(env, e))
            return None
        case SAssign(x, e):
            env[x] = eval_expr(env, e)
            return None
        case SIf(test, body, orelse):
            if eval_expr(env, test):
                return eval_stmts(env, body)
            else:
                return eval_stmts(env, orelse)
        case SWhile(test, body):
            while eval_expr(env, test):
                res = eval_stmts(env, body)
                if res is not None:
                    return res
            return None
        case SReturn(e):
            return eval_expr(env, e)

def eval_stmts(env: RTEnv, ss: IList[Stmt]) -> Optional[Value]:
    for s in ss:
        v = eval_stmt(env, s)
        if v is not None:
            return v
    return None

def eval_decl(env: RTEnv, d: Decl):
    match d:
        case DFun(name, params, _, body):
            param_names = IList([x for (x, _) in params])
            env[name] = VFun(param_names, body, env)

def eval_prog(p: Program):
    env: RTEnv = dict()
    for d in p.decls:
        eval_decl(env, d)
    eval_stmts(env, p.main_body)
