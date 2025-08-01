from ast import Tuple
import ast_4_conv_ass as src
import ast_5_closures as tgt
from identifier import Id
from label import Label
from types_ import *
from util.immutable_list import *

# BEGIN

def closure_conv(p: src.Program) -> tgt.Program:
    decls_out = []
    for d in p:
        closure_conv_decl(decls_out, d)
    return IList(decls_out)

def closure_conv_decl(decls_out: list[tgt.Decl], d: src.Decl):
    match d:
        case src.DFun(name, params, body):
            new_params = ilist(Id.fresh("closure")) + params
            new_body = closure_conv_stmts(decls_out, body)
            decls_out.append(tgt.DFun(name, new_params, new_body))

def closure_conv_stmts(decls_out: list[tgt.Decl], ss: IList[src.Stmt]) -> IList[tgt.Stmt]:
    return IList([closure_conv_stmt(decls_out, s) for s in ss])

def closure_conv_stmt(decls_out: list[tgt.Decl], s: src.Stmt) -> tgt.Stmt:
    match s:
        case src.SExpr(e):
            e = closure_conv_expr(decls_out, e)
            return tgt.SExpr(e)
        case src.SPrint(e):
            e = closure_conv_expr(decls_out, e)
            return tgt.SPrint(e)
        case src.SAssign(lhs, e):
            lhs = closure_conv_lhs(decls_out, lhs)
            e = closure_conv_expr(decls_out, e)
            return tgt.SAssign(lhs, e)
        case src.SIf(e, b1, b2):
            e = closure_conv_expr(decls_out, e)
            b1 = closure_conv_stmts(decls_out, b1)
            b2 = closure_conv_stmts(decls_out, b2)
            return tgt.SIf(e, b1, b2)
        case src.SWhile(e, b):
            e = closure_conv_expr(decls_out, e)
            b = closure_conv_stmts(decls_out, b)
            return tgt.SWhile(e, b)
        case src.SReturn(e):
            e = closure_conv_expr(decls_out, e)
            return tgt.SReturn(e)

def closure_conv_lhs(decls_out: list[tgt.Decl], lhs: src.Lhs) -> tgt.Lhs:
    match lhs:
        case src.LId(x):
            return tgt.LId(x)
        case src.LSubscript(e, i):
            return tgt.LSubscript(closure_conv_expr(decls_out, e), i)

def closure_conv_expr(decls_out: list[tgt.Decl], e: src.Expr) -> tgt.Expr:
    match e:
        case src.EConst(c, size):
            return tgt.EConst(c, size)
        case src.EVar(x):
            return tgt.EVar(x)
        case src.EInput():
            return tgt.EInput()
        case src.EOp1(op, e1):
            e1 = closure_conv_expr(decls_out, e1)
            return tgt.EOp1(op, e1)
        case src.EOp2(e1, op, e2):
            e1 = closure_conv_expr(decls_out, e1)
            e2 = closure_conv_expr(decls_out, e2)
            return tgt.EOp2(e1, op, e2)
        case src.EIf(e1, e2, e3):
            e1 = closure_conv_expr(decls_out, e1)
            e2 = closure_conv_expr(decls_out, e2)
            e3 = closure_conv_expr(decls_out, e3)
            return tgt.EIf(e1, e2, e3)
        case src.ETuple(es):
            return tgt.ETuple(closure_conv_exprs(decls_out, es))
        case src.ETupleAccess(e, i):
            return tgt.ETupleAccess(closure_conv_expr(decls_out, e), i)
        case src.ETupleLen(e):
            return tgt.ETupleLen(closure_conv_expr(decls_out, e))
        case src.ECall(e_func, e_args):
            # always returns a closure as Tuple through the following branch src.EFunRef
            e_func_out = closure_conv_expr(decls_out, e_func)
            e_args_out = closure_conv_exprs(decls_out, e_args)
            # The Tuple itself can not be given to the tgt.Call,
            # we need a reference to reference it through a variable
            tmp = Id.fresh("function_body")
            return tgt.EBegin(
                ilist(tgt.SAssign(tgt.LId(tmp), e_func_out)),
                tgt.ECall(tgt.ETupleAccess(tgt.EVar(tmp), 0), ilist(tgt.EVar(tmp)) + e_args_out),
            )
        case src.EFunRef(name):
            return tgt.ETuple(ilist(tgt.EFunRef(name)))
        case src.ELambda(params, body, fvs):
            function_body_label = Label.fresh("function body")
            closure = get_closure(function_body_label, fvs)

            closure_id = Id.fresh("closure with all the live variables")
            fun_body = get_free_variables_from_closure_to_function_body(fvs, closure_id)

            fun_body += ilist(tgt.SReturn(closure_conv_expr(decls_out, body)))

            new_params = ilist(closure_id) + params
            decls_out.append(tgt.DFun(function_body_label, new_params, fun_body))

            return tgt.ETuple(closure)

def get_closure(function_body_label: Label, fvs: IList[Id]) -> IList[tgt.Expr]:
    closure: IList[tgt.Expr] = ilist(tgt.EFunRef(function_body_label))
    for x in fvs:
        closure += ilist(tgt.EVar(x))
    return closure

def get_free_variables_from_closure_to_function_body(fvs: IList[Id], closure_id: Id) -> IList[tgt.Stmt]:
    fun_body: IList[tgt.Stmt] = ilist()
    for i, x in enumerate(fvs):
        fun_body += ilist(
            tgt.SAssign(tgt.LId(x), tgt.ETupleAccess(tgt.EVar(closure_id), i+1))
        )
    return fun_body

def closure_conv_exprs(decls_out: list[tgt.Decl], es: IList[src.Expr]) -> IList[tgt.Expr]:
    return IList([closure_conv_expr(decls_out, e) for e in es])

# END
