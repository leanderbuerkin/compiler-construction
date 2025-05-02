from itertools import count
from dataclasses import dataclass

from register import *
from label import Label
from identifier import Id
import ast_3_sel as src
import ast_4_mem as tgt
from util.undirected_graph import UndirectedGraph
from util.priority_queue import PriorityQueue
from util.immutable_list import ilist

# API

@dataclass
class RegAllocOutput:
    env: dict[Id, Register | tgt.Offset] # for the assign homes pass
    offset: int # for the prelude and conclusion pass
    callee_saved: set[Register]

def allocate_registers(p: src.Program) -> RegAllocOutput:
    interference = liveness_and_interference_graph(p)
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


def liveness_and_interference_graph(p: src.Program) -> UndirectedGraph[Node]:
    ...

def color_graph(graph: UndirectedGraph[Node]) -> dict[Id, Color]:
    ...

def assign_locations(coloring: dict[Id, Color]) -> RegAllocOutput:
    ...
