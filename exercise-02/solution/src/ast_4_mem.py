from dataclasses import dataclass
from typing import Literal

from register import Register
from label import Label
from types_ import *
from util.immutable_list import IList

# Constants
@dataclass
class Const:
    value: int

# Arguments
type ArgWrite = Register | Offset
type ArgRead = ArgWrite | Const

# Instructions
type Instr = Move | Call | Instr2 

@dataclass(frozen=True)
class Offset:
    reg: Register
    offset: int

    def __str__(self) -> str:
        return f"{self.offset}({self.reg})"

# Move Instruction
@dataclass(frozen=True)
class Move:
    dst: ArgWrite
    src: ArgRead

# Call Instruction
@dataclass(frozen=True)
class Call:
    label: Label

# Binary Instructions
type Instr2Name = Literal["add", "sub"]

@dataclass(frozen=True)
class Instr2:
    name: Instr2Name
    dst: ArgWrite
    src1: ArgRead
    src2: ArgRead

# Programs
type Program = IList[Instr]

# Pretty Printing
def indent(s: str) -> str:
    return "\n".join(4 * " " + l for l in s.splitlines())

def pretty(p: Program) -> str:
    return "\n".join(pretty_instr(i) for i in p)

def pretty_instr(i: Instr) -> str:
    match i:
        case Move(dst, src):
            return f"\tmv\t{pretty_arg(dst)}, {pretty_arg(src)}"
        case Call(l):
            return f"\tcall\t{l}"
        case Instr2(nm, dst, src1, src2):
            return f"\t{nm}\t{pretty_arg(dst)}, {pretty_arg(src1)}, {pretty_arg(src2)}"

def pretty_arg(a: ArgRead) -> str:
    match a:
        case Register(r):
            return r
        case Offset(ro, o):
            return f"{o}({pretty_arg(ro)})"
        case Const(x):
            return str(x)
        case Label(l):
            return l
