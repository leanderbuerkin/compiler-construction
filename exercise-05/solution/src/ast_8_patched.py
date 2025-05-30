from register import *  # noqa
from label import Label
from util.immutable_list import IList

from ast_9_riscv import (
    Const as Const,
    Offset as Offset,
    Instr as Instr,
    Directive as Directive,
    DGlobal as DGlobal,
    RInstrName as RInstrName,
    RInstr as RInstr,
    IInstr2 as IInstr2,
    IInstr1 as IInstr1,
    Load as Load,
    LoadAddress as LoadAddress,
    Store as Store,
    Call as Call,
    Jump as Jump,
    BranchName as BranchName,
    Branch as Branch,
    Return as Return,
    pretty_arg as pretty_arg,
    pretty_instr as pretty_instr,
)

type Block = IList[Instr]
type Blocks = dict[Label, Block]
type Program = Blocks


def pretty_block(b: Block) -> str:
    return "\n".join(pretty_instr(i) for i in b)


def pretty(p: Program) -> str:
    return "\n".join(f"{lab}:\n{pretty_block(p[lab])}" for lab in p)
