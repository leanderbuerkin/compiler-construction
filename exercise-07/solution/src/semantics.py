from dataclasses import dataclass
from typing import Optional


from ast_1_python import *
from util.immutable_list import IList, ilist

from identifier import Id

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

type Value = int | bool | None | VTuple | VFunction

# Value Environment

@dataclass(frozen=True)
class RTEnv:
    current: dict[Id, Value]
    parent: Optional['RTEnv']

def lookup(cur: Optional[RTEnv], x: Id) -> Value:
    while cur is not None and x not in cur.current.keys():
        cur = cur.parent
    if cur is None:
        raise Exception(f"Identifier not found {x}")
    else:
        return cur.current[x]

def assign(env: RTEnv, x: Id, v: Value) -> None:
    env.current[x] = v

@dataclass
class VTuple:
    entries: list[Value]

@dataclass
class VFunction:
    name: Id
    xs: IList[Id]
    body: IList[Stmt]
    env: RTEnv

# Evaluation

def apply_fun(f: Value, xs: tuple[Value, ...]) -> Optional[Value]:
    match f:
        case VFunction(_, parms, body, env):
            fenv = RTEnv(dict(zip(parms, xs)), env)
            return eval_list_stmt(fenv, body)
        case _:
            raise Exception('apply_fun: unexpected value ' + repr(f))

def eval_expr(env: RTEnv, e: Expr) -> Value:
    match e:
        case EConst(c):
            return c
        case EVar(x):
            return lookup(env, x)
        case EOp1(op, e):
            v = eval_expr(env, e)
            match v:
                case VTuple(_) | VFunction() | None:
                    raise Exception("Unary operator '{op}' not allowed for '{pretty_expr(e)}'")
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
                case (int(x1) | bool(x1)), (int(x2) | bool(x2)): # type: ignore
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
                            return v1 == v2
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
        case ECall(func, args):
            f = eval_expr(env, func)
            xs = tuple(eval_expr(env, x) for x in args)
            match apply_fun(f, xs):
                case None:
                    raise Exception("Tried to use void function in expressions")
                case v:
                    return v
        case ELambda(xs, expr):
            return VFunction(Id("lambda"), xs, ilist(SReturn(expr)), env)

def eval_list_stmt(env: RTEnv, ss: IList[Stmt]) -> Optional[Value]:
    for s in ss:
        match s:
            case SExpr(e):
                eval_expr(env, e)
            case SPrint(e):
                print(eval_expr(env, e))
            case SAssign(x, _, e):
                assign(env, x, eval_expr(env, e))
            case SIf(test, body, orelse):
                tv = eval_expr(env, test)
                match eval_list_stmt(env, body) if tv else eval_list_stmt(env, orelse):
                    case None:
                        continue
                    case rv:
                        return rv
            case SWhile(test, body):
                while eval_expr(env, test):
                    match eval_list_stmt(env, body):
                        case None:
                            continue
                        case rv:
                            return rv
            case SReturn(e):
                return eval_expr(env, e)
    return None

def eval_list_defs(env: RTEnv, defs: IList[Decl]) -> None:
    for d in defs:
        match d:
            case DFun(f, parms, _, body):
                fv = VFunction(f, IList([x for (x, _) in parms]), body, env)
                assign(env, f, fv)

def eval_prog(p: Program) -> None:
    match p:
        case Program(defs, body):
            env: RTEnv = RTEnv(dict(), None)
            eval_list_defs(env, defs)
            eval_list_stmt(env, body)
