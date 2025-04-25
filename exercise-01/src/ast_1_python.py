from dataclasses import dataclass
from typing import Literal

from identifier import Id
from types_ import *
from util.immutable_list import IList

# Unary Operators
type Op1 = Literal["-"]

# Binary Operators
type Op2 = Literal["+", "-"]

# Expressions
type Expr = EConst | EVar | EOp1 | EOp2 | EInput

@dataclass(frozen=True)
class EConst:
    value: int

@dataclass(frozen=True)
class EVar:
    name: Id

@dataclass(frozen=True)
class EOp1:
    op: Op1
    operand: Expr

@dataclass(frozen=True)
class EOp2:
    left: Expr
    op: Op2
    right: Expr

@dataclass(frozen=True)
class EInput:
    pass

# Statements
type Stmt = SExpr | SPrint | SAssign

@dataclass(frozen=True)
class SExpr:
    expr: Expr

@dataclass(frozen=True)
class SPrint:
    expr: Expr

@dataclass(frozen=True)
class SAssign:
    lhs: Id
    rhs: Expr

# Programs
type Program = IList[Stmt]

# Pretty Printing
def indent(s: str) -> str:
    return "\n".join(4 * " " + l for l in s.splitlines())

def pretty(p: Program) -> str:
    return pretty_stmts(p)

def pretty_stmts(ss: IList[Stmt]) -> str:
    return "\n".join(pretty_stmt(s) for s in ss)

def pretty_stmt(s: Stmt) -> str:
    match s:
        case SExpr(e):
            return pretty_expr(e)
        case SAssign(x, e):
            return f"{x} = {pretty_expr(e)}"
        case SPrint(e):
            return "print(" + pretty_expr(e) + ")"

def pretty_expr(e: Expr) -> str:
    match e:
        case EConst(x) | EVar(x):
            return str(x)
        case EOp1(op, e):
            return f"{op} {pretty_expr(e)}"
        case EOp2(e1, op, e2):
            return f"({pretty_expr(e1)} {op} {pretty_expr(e2)})"
        case EInput():
            return "input_int()"
