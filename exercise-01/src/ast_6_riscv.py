from dataclasses import dataclass
from typing import Literal

from register import Register
from label import Label
from util.immutable_list import IList

# Constants
type Const = int

# Offsets
@dataclass(frozen=True)
class Offset:
    reg: Register
    offset: int

# Instructions
type Instr = Label | Load | Store | RInstr | IInstr2 | IInstr1 \
           | Call | Return | Directive

# Assembler Directives
type Directive = DGlobal

# .globl LABEL
@dataclass(frozen=True)
class DGlobal:
    label: Label

# Register Instructions
type RInstrName = Literal["add", "sub"]

@dataclass(frozen=True)
class RInstr:
    name: RInstrName  # name of the instruction
    rd: Register  # destination register
    rs1: Register  # source register 1
    rs2: Register  # source register 2

# Binary Immediate Instructions
type IInstr2Name = Literal["addi"]

@dataclass(frozen=True)
class IInstr2:
    name: IInstr2Name  # name of the instruction
    rd: Register  # destination register
    rs: Register  # source register
    imm: int  # immediate value

# Unary Immediate Instructions
type IInstr1Name = Literal["li"]

@dataclass(frozen=True)
class IInstr1:
    name: IInstr1Name  # name of the instruction
    rd: Register  # destination register
    imm: int  # immediate value

# Memory Instructions
# ld DST,SRC
@dataclass(frozen=True)
class Load:
    dst: Register
    src: Offset

# sd SRC,DST
@dataclass(frozen=True)
class Store:
    src: Register
    dst: Offset

# Control Flow Instructions
# call
@dataclass(frozen=True)
class Call:
    target: Label

# ret
@dataclass(frozen=True)
class Return:
    pass

# Programs
type Program = IList[Instr]

# Pretty Printing
def pretty_arg(a: Register | Offset | Const | Label) -> str:
    match a:
        case Register(r):
            return r
        case Offset(r, o):
            return f"{o}({r.name})"
        case Label(l):
            return f"{l}"
        case int(i):
            return f"{i}"

def pretty_instr(i: Instr) -> str:
    match i:
        case Label(l):
            return f"{l}: "
        case Load(dst, src):
            return f"\tld\t{pretty_arg(dst)},{pretty_arg(src)}"
        case Store(dst, src):
            return f"\tsd\t{pretty_arg(dst)},{pretty_arg(src)}"
        case RInstr(nm, dst, src1, src2):
            return f"\t{nm}\t{pretty_arg(dst)},{pretty_arg(src1)},{pretty_arg(src2)}"
        case IInstr2(nm, dst, src, imm):
            return f"\t{nm}\t{pretty_arg(dst)},{pretty_arg(src)},{pretty_arg(imm)}"
        case IInstr1(nm, dst, imm):
            return f"\t{nm}\t{pretty_arg(dst)},{pretty_arg(imm)}"
        case Call(l):
            return f"\tcall\t{l}"
        case Return():
            return "\tret"
        case DGlobal(l):
            return f"\n\t.globl\t{l}"

def pretty(p: Program) -> str:
    return "\n".join(pretty_instr(i) for i in p)
