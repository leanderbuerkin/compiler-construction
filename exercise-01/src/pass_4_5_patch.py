import ast_4_mem as src
import ast_5_patched as tgt
from register import *
from util.immutable_list import ilist

def patch_instructions(p: src.Program) -> tgt.Program:
    ...