from itertools import count
from dataclasses import dataclass

from register import *
from label import Label
from identifier import Id
import ast_5_sel as src
import ast_6_mem as tgt
from util.directed_graph import DirectedGraph
from util.undirected_graph import UndirectedGraph
from util.priority_queue import PriorityQueue
from util.immutable_list import ilist

# API

@dataclass
class RegAllocOutput:
    env: dict[Id, Register | tgt.Offset]
    offset: int
    callee_saved: set[Register]

def allocate_registers(p: src.Program) -> RegAllocOutput:
    cfg = control_flow_graph(p)
    interference = liveness_and_interference_graph(p, cfg)
    coloring = color_graph(interference)
    return assign_locations(coloring)

# Implementation

REG_ORDER = ilist(
    # can not be used for register allocation
    zero, sp, fp, tp, gp, ra, t0, t1,
    # can be used for register allocation
    a0, a1, a2, a3, a4, a5, a6, a7,
    s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11,
    t2, t3, t4, t5, t6,
)

REGISTER_TO_COLOR = {r: i - 8 for i, r in enumerate(REG_ORDER)}
COLOR_TO_REGISTER = {v: k for k, v in REGISTER_TO_COLOR.items()}

type Color = int  # colors are represented by natural numbers
type Node = Id | Register  # nodes in the inference graph

# the read set of an argument in read position
def read_set_src_arg(arg: src.ArgRead) -> set[Node]:
    match arg:
        case Register(_):
            return {arg}
        case Id(_):
            return {arg}
        case src.Const(_):
            return set()

# the read set of an argument in write position
def read_set_dst_arg(_: src.ArgWrite) -> set[Node]:
    return set()

# the write set of an argument in read position is always empty
def write_set_src_arg(_: src.ArgRead) -> set[Node]:
    return set()

# the write set of an argument in write position
def write_set_dst_arg(arg: src.ArgWrite) -> set[Node]:
    match arg:
        case Register(_):
            return {arg}
        case Id(_):
            return {arg}

# the read set of an instruction
def read_set(i: src.Instr) -> set[Node]:
    match i:
        case src.Move(rd, rs):
            return read_set_dst_arg(rd) | read_set_src_arg(rs)
        case src.Call(_, arity):
            return set(FUNCTION_ARG_REGISTERS[:arity])
        case src.Instr2(_, rd, rs1, rs2):
            return read_set_dst_arg(rd) | read_set_src_arg(rs1) | read_set_src_arg(rs2)
        case src.Branch(_, rs1, rs2, _):
            ...
        case src.Jump(_):
            ...

# the write set of an instruction
def write_set(i: src.Instr) -> set[Node]:
    match i:
        case src.Move(rd, rs):
            return write_set_dst_arg(rd) | write_set_src_arg(rs)
        case src.Call(_):
            return set(CALLER_SAVED_REGISTERS)
        case src.Instr2(_, rd, rs1, rs2):
            return write_set_dst_arg(rd) | write_set_src_arg(rs1) | write_set_src_arg(rs2)
        case src.Branch(_, rs1, rs2, _):
            ...
        case src.Jump(_):
            ...

def control_flow_graph(p: src.Blocks) -> DirectedGraph[Label]:
    ...

def liveness_and_interference_graph(p: src.Program, cfg: DirectedGraph[Label]) -> UndirectedGraph[Node]:
    ...

def color_graph(graph: UndirectedGraph[Node]) -> dict[Id, Color]:
    colors: dict[Id, Color] = {}
    saturation: dict[Id, set[Color]] = {n: set() for n in graph.nodes() if type(n) is Id}
    queue: PriorityQueue[Id] = PriorityQueue()

    for n in graph.nodes():
        match n:
            case Id(_):
                for x in graph.neighbors(n):
                    match x:
                        case Register(_):
                            saturation[n] |= {REGISTER_TO_COLOR[x]}
                        case _:
                            pass
                queue.push(n, len(saturation[n]))

    while queue:
        head = queue.pop()
        sat = saturation[head]
        color = next(x for x in count() if x not in sat)

        for x in graph.neighbors(head):
            match x:
                case Id(_):
                    if color not in saturation[x]:
                        queue.increment(x)
                        saturation[x] |= {color}

        colors[head] = color

    return colors

def assign_locations(coloring: dict[Id, Color]) -> RegAllocOutput:
    env: dict[Id, Register | tgt.Offset] = {}
    offset: int = 16
    callee_saved: set[Register] = set()

    for color in coloring.values():
        if color in COLOR_TO_REGISTER:
            reg = COLOR_TO_REGISTER[color]
            if reg in CALLEE_SAVED_REGISTERS:
                callee_saved.add(reg)

    offset += len(callee_saved) * 8

    mapping: dict[Color, tgt.Offset] = {}

    for id, color in coloring.items():
        if color in COLOR_TO_REGISTER:
            env[id] = COLOR_TO_REGISTER[color]
        else:
            if color in mapping:
                env[id] = mapping[color]
            else: 
                offset += 8
                off = tgt.Offset(fp, -offset)
                env[id] = off
                mapping[color] = off

    return RegAllocOutput(env, offset, callee_saved)
