import ast_2_mon as src
import ast_3_sel as tgt
from identifier import Id
from label import Label
from register import *
from util.immutable_list import ilist, IList

def select(p: src.Program) -> tgt.Program:
    ...
