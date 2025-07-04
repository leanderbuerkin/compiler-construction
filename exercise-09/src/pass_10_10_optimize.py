import ast_10_mem as src
import ast_10_mem as tgt
from util.immutable_list import IList, ilist

def optimize(p: src.Program) -> tgt.Program:
    return IList([optimize_fun(f) for f in p])

def optimize_fun(f: src.Function) -> tgt.Function:
    return tgt.Function(
        f.entry_label,
        f.start_label,
        f.end_label,
        optimize_blocks(f.body, f.entry_label)
    )

def optimize_blocks(blocks: src.Blocks, entry_label: src.Label) -> tgt.Blocks:
    blocks_out1 = {l: optimize_block(b) for (l, b) in blocks.items()}
    
    # Remove unreachable blocks
    ...

def optimize_block(block: src.Block) -> tgt.Block:
    block_out1: src.Block = ilist()
    i = 0
    while i < len(block):
        match block[i]:
            case src.Instr2(op, dst, src.Const(val1, size1), src.Const(val2, size2)):
                ...
            case src.Instr2(op, dst, src1, src.Const(val1, size1)):
                ...
            case src.Branch(cc, src.Const(val1, size1), src.Const(val2, size2), target):
                ...
            case _:
                block_out1 += ilist(block[i])
        i += 1

    block_out2: src.Block = ilist()
    i = 0
    while i < len(block_out1):
        match block[i]:
            case src.Move(dst1, src1):
                ...
            case _:
                block_out2 += ilist(block_out1[i])
        i += 1
    return block_out2

def to_int_64(value: int, size: str) -> int:
    return value << (1 if size == "63bit" else 0)

def simulate_over_and_underflow(i: int) -> int:
    while i > 2**63 - 1:
        i = i - (2**64)
    while i < -(2**63):
        i = i + (2**64)
    return i