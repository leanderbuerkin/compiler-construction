from dataclasses import dataclass
from typing import Literal

from identifier import Id
from util.immutable_list import IList

# Unary Operators
type Op1 = Literal["-", "not"]

# Binary Operators
type Op2 = Literal["+", "-", "==", "!=", "<=", "<", ">", ">="]

# Global Variables
type Global = Literal['gc_free_ptr', 'gc_fromspace_end']

# Expressions
type Expr = EConst | EVar | EOp1 | EOp2 | EInput | EIf | ETupleAccess | ETupleLen | EBegin | EAllocate | EGlobal

@dataclass(frozen=True)
class EConst:
    value: int | bool
    size: Literal['64bit', '63bit']

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

@dataclass(frozen=True)
class EIf:
    test: Expr
    body: Expr
    orelse: Expr

@dataclass(frozen=True)
class ETupleAccess:
    e: Expr
    index: int

@dataclass(frozen=True)
class ETupleLen:
    e: Expr

@dataclass(frozen=True)
class EBegin:
    body: IList['Stmt']
    tail: Expr

@dataclass(frozen=True)
class EAllocate:
    num_elems: int

@dataclass(frozen=True)
class EGlobal:
    var: Global

# Left-hand sides of Assign Statements
type Lhs = LId | LSubscript

@dataclass
class LId:
    id: Id

@dataclass
class LSubscript:
    e: Expr
    offset: int

# Statements
type Stmt = SExpr | SPrint | SAssign | SIf | SWhile | SCollect

@dataclass(frozen=True)
class SExpr:
    expr: Expr

@dataclass(frozen=True)
class SPrint:
    expr: Expr

@dataclass(frozen=True)
class SAssign:
    lhs: Lhs
    rhs: Expr

@dataclass(frozen=True)
class SIf:
    test: Expr
    body: IList[Stmt]
    orelse: IList[Stmt]

@dataclass(frozen=True)
class SWhile:
    test: Expr
    body: IList[Stmt]

@dataclass(frozen=True)
class SCollect:
    num_words: int

# Programs
type Program = IList[Stmt]

# Pretty Printing
def indent(s: str) -> str:
    return "\n".join(4 * " " + l for l in s.splitlines())

def pretty(p: Program) -> str:
    return "\n".join(pretty_stmt(s) for s in p)

def pretty_stmt(s: Stmt) -> str:
    match s:
        case SExpr(e):
            return pretty_expr(e)
        case SAssign(lhs, e):
            return pretty_lhs(lhs) + " = " + pretty_expr(e)
        case SPrint(e):
            return "print(" + pretty_expr(e) + ")"
        case SIf(test, body, orelse):
            return f"if {pretty_expr(test)}:\n" \
                   f"{indent(pretty(body))}\n" \
                   f"else:\n" \
                   f"{indent(pretty(orelse))}"
        case SWhile(test, body):
            return f"while {pretty_expr(test)}:\n{indent(pretty(body))}"
        case SCollect(num_words):
            return f"collect({num_words})"

def pretty_lhs(lhs: Lhs) -> str:
    match lhs:
        case LId(x):
            return str(x)
        case LSubscript(e, i):
            return f"{pretty_expr(e)}[{i}]"

def pretty_expr(e: Expr) -> str:
    match e:
        case EVar(x):
            return str(x)
        case EConst(x, size):
            return str(x) + ("" if size == "64bit" else "°")
        case EOp1(op, e):
            return f"{op} {pretty_expr(e)}"
        case EOp2(e1, op, e2):
            return f"({pretty_expr(e1)} {op} {pretty_expr(e2)})"
        case EInput():
            return "input_int()"
        case EIf(test, body, orelse):
            return f"({pretty_expr(body)} if {pretty_expr(test)} else {pretty_expr(orelse)})"
        case ETupleAccess(e, i):
            return f"{pretty_expr(e)}[{i}]"
        case ETupleLen(e):
            return f"len({pretty_expr(e)})"
        case EBegin(ss, e):
            ss_str = "\n".join(pretty_stmt(s) for s in ss)
            return "begin {\n" + indent(f"{ss_str}\n{pretty_expr(e)}\n}}")
        case EGlobal(g):
            return "@" + g
        case EAllocate(n):
            return f"allocate({n})"
        case ETupleAccess(e, i):
            return f"{pretty_expr(e)}[{i}]"
        case ETupleLen(e):
            return f"len({pretty_expr(e)})"
