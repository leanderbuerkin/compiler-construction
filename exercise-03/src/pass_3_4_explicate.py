import ast_3_mon as src
import ast_4_exp as tgt
from util.immutable_list import IList, ilist
from label import Label

def explicate(p: src.Program, start_label: Label = Label("main"), exit_label: Label = Label("exit")) -> tgt.Program:
    ...