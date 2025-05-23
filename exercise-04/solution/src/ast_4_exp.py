from dataclasses import dataclass
from typing import Literal

from identifier import Id
from label import Label
from types_ import *
from util.immutable_list import IList

# Unary Operators
type Op1 = Literal["-", "not"]

# Binary Operators
type Op2Arith = Literal["+", "-"]
type Op2Comp = Literal["==", "!=", "<=", "<", ">", ">="]


# Atomic Expressions
type ExprAtom = EConst | EVar

@dataclass(frozen=True)
class EConst:
    value: int | bool

@dataclass(frozen=True)
class EVar:
    name: Id

# Complex Expressions
type Expr = ExprAtom | EOp1 | EOp2Arith | EInput | EOp2Comp

@dataclass(frozen=True)
class EOp1:
    op: Op1
    operand: ExprAtom

@dataclass(frozen=True)
class EOp2Arith:
    left: ExprAtom
    op: Op2Arith
    right: ExprAtom

@dataclass(frozen=True)
class EOp2Comp:
    left: ExprAtom
    cmp: Op2Comp
    right: ExprAtom

@dataclass(frozen=True)
class EInput:
    pass

# Statements
type Stmt = SPrint | SAssign | SIf | SGoto

@dataclass(frozen=True)
class SPrint:
    expr: ExprAtom

@dataclass(frozen=True)
class SAssign:
    lhs: Id
    rhs: Expr

@dataclass(frozen=True)
class SIf:
    test: EOp2Comp
    body: Label
    orelse: Label


@dataclass(frozen=True)
class SGoto:
    target: Label

# Programs
type Block = IList[Stmt]
type Blocks = dict[Label, Block]
type Program = Blocks

# Pretty Printing
def indent(s: str) -> str:
    return "\n".join(4 * " " + l for l in s.splitlines())

def pretty(p: Program) -> str:
    return "\n".join(
                f"{lab}:\n\t" + pretty_block(block)
                for lab, block in p.items()
            )

def pretty_block(p: Block) -> str:
    return "\n\t".join(pretty_stmt(s) for s in p)

def pretty_stmt(s: Stmt) -> str:
    match s:
        case SAssign(lhs, e):
            return str(lhs) + " = " + pretty_expr(e)
        case SPrint(e):
            return f"print({pretty_expr(e)})"
        case SIf(e, l1, l2):
            return f"if {pretty_expr(e)} {{ goto {l1} }} else {{ goto {l2} }}"
        case SGoto(l):
            return f"goto {l}"

def pretty_expr(e: Expr) -> str:
    match e:
        case EVar(x):
            return str(x)
        case EConst(x):
            return str(x)
        case EOp1("not", e):
            return f"not {pretty_expr(e)}"
        case EOp1(op, e):
            return f"{op}{pretty_expr(e)}"
        case EOp2Arith(e1, op, e2):
            return f"({pretty_expr(e1)} {op} {pretty_expr(e2)})"
        case EInput():
            return "input_int()"
        case EOp2Comp(e1, op, e2):
            return f"({pretty_expr(e1)} {op} {pretty_expr(e2)})"