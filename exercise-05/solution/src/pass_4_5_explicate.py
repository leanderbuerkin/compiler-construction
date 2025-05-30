import ast_4_mon as src
import ast_5_exp as tgt
from util.immutable_list import IList, ilist
from label import Label

def explicate(p: src.Program, start_label: Label = Label("main"), exit_label: Label = Label("exit")) -> tgt.Program:
    out: tgt.Program = dict()
    out[start_label] = ilist()
    l = explicate_stmts(out, start_label, p)
    out[l] += ilist(tgt.SGoto(exit_label))
    return out

def explicate_stmts(out: tgt.Blocks, l: Label, p: IList[src.Stmt]) -> Label:
    for s in p:
        l = explicate_stmt(out, l, s)
    return l

def explicate_stmt(out: tgt.Blocks, l: Label, s: src.Stmt) -> Label:
    match s:
        case src.SAssign(lhs, e):
            lhs_out = explicate_lhs(lhs)
            e_out = explicate_expr(e)
            out[l] += ilist(tgt.SAssign(lhs_out, e_out))
            return l
        case src.SPrint(e):
            out[l] += ilist(tgt.SPrint(explicate_atom(e)))
            return l
        case src.SIf(src.EOp2Comp(a1, op, a2), b1, b2):
            body_label: Label = Label.fresh("body")
            orelse_label: Label = Label.fresh("orelse")
            cont_label: Label = Label.fresh("cont")

            test = tgt.EOp2Comp(explicate_atom(a1), op, explicate_atom(a2))
            out[l] += ilist(tgt.SIf(test, body_label, orelse_label))

            out[body_label] = ilist()
            out[orelse_label] = ilist()
            body_label_out = explicate_stmts(out, body_label, b1)
            orelse_label_out = explicate_stmts(out, orelse_label, b2)

            out[body_label_out] += ilist(tgt.SGoto(cont_label))
            out[orelse_label_out] += ilist(tgt.SGoto(cont_label))

            out[cont_label] = ilist()
            return cont_label
        case src.SWhile(test_prelude, src.EOp2Comp(a1, op, a2), b):
            test_label = Label.fresh("test")
            body_label = Label.fresh("body")
            cont_label = Label.fresh("cont")

            # Finish current block with goto to `test_label`.
            out[l] += ilist(tgt.SGoto(test_label))

            # Create one (or more) blocks for the condition.
            out[test_label] = ilist()
            test_label_out = explicate_stmts(out, test_label, test_prelude)
            test = tgt.EOp2Comp(explicate_atom(a1), op, explicate_atom(a2))
            out[test_label_out] += ilist(tgt.SIf(test, body_label, cont_label))

            # Create a new block for the body, which should jump
            # to the `test_prelude_label` after running.
            out[body_label] = ilist()
            body_label_out = explicate_stmts(out, body_label, b)
            out[body_label_out] += ilist(tgt.SGoto(test_label))

            # Continue with a new block at `cont_label`
            out[cont_label] = ilist()
            return cont_label
        case src.SCollect(n):
            out[l] += ilist(tgt.SCollect(n))
            return l

def explicate_lhs(lhs: src.Lhs) -> tgt.Lhs:
    match lhs:
        case src.LId(x):
            return tgt.LId(x)
        case src.LSubscript(e, i):
            return tgt.LSubscript(explicate_atom(e), i)

def explicate_expr(e: src.Expr) -> tgt.Expr:
    match e:
        case src.EVar(_) | src.EConst(_):
            return explicate_atom(e)
        case src.EInput():
            return tgt.EInput()
        case src.EOp1(op, a):
            e_out = explicate_atom(a)
            return tgt.EOp1(op, e_out)
        case src.EOp2Arith(a1, op, a2):
            a1_out = explicate_atom(a1)
            a2_out = explicate_atom(a2)
            return tgt.EOp2Arith(a1_out, op, a2_out)
        case src.EOp2Comp(a1, op, a2):
            a1_out = explicate_atom(a1)
            a2_out = explicate_atom(a2)
            return tgt.EOp2Comp(a1_out, op, a2_out)
        case src.EGlobal(x):
            return tgt.EGlobal(x)
        case src.EAllocate(n):
            return tgt.EAllocate(n)
        case src.ETupleLen(e1):
            e1_out = explicate_atom(e1)
            return tgt.ETupleLen(e1_out)
        case src.ETupleAccess(e1, i):
            e1_out = explicate_atom(e1)
            return tgt.ETupleAccess(e1_out, i)

def explicate_atom(a: src.ExprAtom) -> tgt.ExprAtom:
    match a:
        case src.EVar(x):
            return tgt.EVar(x)
        case src.EConst(x, size):
            return tgt.EConst(x, size)

