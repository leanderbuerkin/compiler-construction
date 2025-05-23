from ast_1_python import *
from util.immutable_list import IList
from identifier import Id

# Simulate Integer Overflow Behavior
MAX_INT_64 = 2**63 - 1
MIN_INT_64 = -(2**63)

def simulate_over_and_underflow(i: int) -> int:
    while i > MAX_INT_64:
        i = i - (2**64)
    while i < MIN_INT_64:
        i = i + (2**64)
    return i

# Values
type Value = int | bool

# Value Environment
type RTEnv = dict[Id, Value]

def lookup(cur: RTEnv, x: Id) -> Value:
    if x not in cur:
        raise Exception(f"Identifier not found {x}")
    else:
        return cur[x]

def assign(env: RTEnv, x: Id, v: Value) -> None:
    env[x] = v

# Evaluation
def eval_expr(env: RTEnv, e: Expr) -> Value:
    match e:
        case EConst(c):
            return c
        case EVar(x):
            return lookup(env, x)
        case EOp1(op, e):
            v = eval_expr(env, e)
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
                case int(x1), int(x2):
                    match op:
                        case "+":
                            return simulate_over_and_underflow(x1 + x2)
                        case "-":
                            return simulate_over_and_underflow(x1 - x2)
                        case "<=":
                            return x1 <= x2
                        case "<":
                            return x1 < x2
                        case ">":
                            return x1 > x2
                        case ">=":
                            return x1 >= x2
                        case _:
                            pass 
            match v1, v2: 
                case (int(x1) | bool(x1)), (int(x2) | bool(x2)): # type: ignore
                    match op:
                        case "==":
                            return x1 == x2
                        case "!=":
                            return x1 != x2
                        case _:
                            raise Exception("Impossible!")                        
                case _:
                    raise Exception("Impossible!")
        case EInput():
            while True:
                try:
                    res = int(input())
                    return simulate_over_and_underflow(res)
                except ValueError:
                    continue
        case EIf(test, body, orelse):
            v1 = eval_expr(env, test)
            if v1:
                return eval_expr(env, body)
            else:
                return eval_expr(env, orelse)

def eval_stmts(env: RTEnv, ss: IList[Stmt]) -> None:
    for s in ss:
        match s:
            case SExpr(e):
                eval_expr(env, e)
            case SPrint(e):
                print(eval_expr(env, e))
            case SAssign(x, e):
                assign(env, x, eval_expr(env, e))
            case SIf(test, body, orelse):
                if eval_expr(env, test):
                    eval_stmts(env, body)
                else:
                    eval_stmts(env, orelse)
            case SWhile(test, body):
                while eval_expr(env, test):
                    eval_stmts(env, body)

def eval_prog(p: Program) -> None:
    env: RTEnv = dict()
    eval_stmts(env, p)
