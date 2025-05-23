from dataclasses import dataclass
from typing import Literal

from identifier import Id
from label import Label
from register import Register
from types_ import *
from util.immutable_list import IList

# Constants
@dataclass
class Const:
    value: int
    size: Literal['63bit', '64bit']

# Arguments
type ArgWrite = Id | Register | Offset
type ArgRead = ArgWrite | Const

# Memory Access
@dataclass(frozen=True)
class Offset:
    reg: Register | Id | Label
    offset: int

    def __str__(self) -> str:
        return f"{self.offset}({self.reg})"

# Instructions
type Instr = Move | Call | Jump | Branch | Instr2 

@dataclass(frozen=True)
class Move:
    dst: ArgWrite
    src: ArgRead

@dataclass(frozen=True)
class Call:
    target: Label
    arity: int

@dataclass(frozen=True)
class Jump:
    label: Label

type BranchName = Literal["beq", "bne", "blt", "bge"]

@dataclass(frozen=True)
class Branch:
    name: BranchName
    src1: ArgRead
    src2: ArgRead
    target: Label

type Instr2Name = Literal["add", "sub", "mul", "div", "xor", "sltu", "slt", "and", "sll", "srl"]

@dataclass(frozen=True)
class Instr2:
    name: Instr2Name 
    dst: ArgWrite
    src1: ArgRead
    src2: ArgRead

# Programs
type Block = IList[Instr]
type Blocks = dict[Label, Block]
type Program = Blocks

# Pretty Printing
def indent(s: str) -> str:
    return "\n".join(4 * " " + l for l in s.splitlines())

def pretty(p: Program) -> str:
    return "\n".join([f"{lab}:\n{pretty_block(p[lab])}" for lab in p])

def pretty_block(b: Block) -> str:
    return "\n".join([pretty_instr(i) for i in b])

def pretty_instr(i: Instr) -> str:
    match i:
        case Move(dst, src):
            return f"\tmv\t{pretty_arg(dst)},{pretty_arg(src)}"
        case Call(l):
            return f"\tcall\t{l}"
        case Jump(l):
            return f"\tj\t{l}"
        case Branch(cc, src1, src2, target):
            return f"\t{cc}\t{pretty_arg(src1)},{pretty_arg(src2)},{target}"
        case Instr2(nm, dst, src1, src2):
            return f"\t{nm}\t{pretty_arg(dst)},{pretty_arg(src1)},{pretty_arg(src2)}"

def pretty_arg(a: ArgRead) -> str:
    match a:
        case Register(r):
            return r
        case Id(r):
            return r
        case Const(x, size):
            return str(x) + ("" if size == "64bit" else "°")
        case Offset(ro, o):
            return f"{o}({str(ro)})"
