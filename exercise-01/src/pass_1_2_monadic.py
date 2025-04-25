import ast_1_python as src
import ast_2_mon as tgt
from identifier import Id
from util.immutable_list import IList, ilist

def monadic(p: src.Program) -> tgt.Program:
    ...