import ast_3_sel as src
import ast_4_mem as tgt
from identifier import Id
from register import *
from util.immutable_list import ilist

def assign_homes(p: src.Program,) ->  tuple[tgt.Program, int]:
    # the returned integer should be the size of the stack frame
    ...