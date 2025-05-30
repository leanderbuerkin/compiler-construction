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
    size: Literal['63bit', '64bit']

# Arguments
type ArgWrite = Register | Offset
type ArgRead = ArgWrite | Const

# Instructions
type Instr = Move | Call | Jump | Branch | Instr2 

# Offset
@dataclass(frozen=True)
class Offset:
    reg: 'Register | Label | Offset'
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

# Jump Instruction
@dataclass(frozen=True)
class Jump:
    label: Label

# Branch Instructions
type BranchName = Literal["beq", "bne", "blt", "bge"]

@dataclass(frozen=True)
class Branch:                                  
    name: BranchName
    src1: ArgRead
    src2: ArgRead
    target: Label

# Binary Instructions
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
    return "\n".join(
        f"{lab}:\n{pretty_block(p[lab])}" for lab in p
    )

def pretty_block(b: Block) -> str:
    return "\n".join(pretty_instr(i) for i in b)

def pretty_instr(i: Instr) -> str:
    match i:
        case Move(dst, src):
            return f"\tmv\t{pretty_arg(dst)}, {pretty_arg(src)}"
        case Call(l):
            return f"\tcall\t{l}"
        case Jump(label):
            return f"\tj\t{label}"
        case Branch(cc, src1, src2, target):
            return f"\t{cc}\t{pretty_arg(src1)}, {pretty_arg(src2)}, {target}"
        case Instr2(nm, dst, src1, src2):
            return f"\t{nm}\t{pretty_arg(dst)}, {pretty_arg(src1)}, {pretty_arg(src2)}"

def pretty_arg(a: ArgRead) -> str:
    match a:
        case Register(r):
            return r
        case Offset(_, _):
            return str(a)
        case Const(x, size):
            return str(x) + ("" if size == "64bit" else "°")
        case Label(l):
            return l
