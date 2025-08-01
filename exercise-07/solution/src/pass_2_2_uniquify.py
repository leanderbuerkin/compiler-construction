from ast import Expr
import ast_2_shrunk as src
import ast_2_shrunk as tgt
from identifier import Id
from util.immutable_list import *

# BEGIN
def uniquify(p: src.Program) -> tgt.Program:
    renaming = {}

    # Keep function names the same
    for d in p:
        match d:
            case src.DFun(name, _, _):
                renaming[name] = name

    return IList([uniquify_decl(renaming.copy(), d) for d in p])

def uniquify_elambda(renaming: dict[Id, Id], params: IList[Id], body: src.Expr
                     ) -> tgt.ELambda:
    local_scope = get_copy_without_params(renaming, params)
    uniquified_params = rename_params(local_scope, params)
    uniquified_body = uniquify_expr(local_scope, body)
    return tgt.ELambda(uniquified_params, uniquified_body)

def uniquify_decl(renaming: dict[Id, Id], d: src.Decl) -> tgt.Decl:
    match d:
        case src.DFun(name, params, body):
            local_scope = get_copy_without_params(renaming, params)
            uniquified_params = rename_params(local_scope, params)
            uniquified_body = uniquify_stmts(local_scope, body)
            return tgt.DFun(name, uniquified_params, uniquified_body)

def get_copy_without_params(renaming: dict[Id, Id], params: IList[Id]
                            ) -> dict[Id, Id]:
    global_scope = renaming.copy()
    return global_scope

def rename_params(renaming: dict[Id, Id], params: IList[Id]) -> IList[Id]:
    renamed_params: IList[Id] = ilist()
    for param in params:
        if param in renaming.keys():
            raise Exception("Parameters should not be present in local scope.")
        renaming[param] = Id.fresh(param.name)
        renamed_params += ilist(renaming[param])
    return renamed_params

def uniquify_stmts(renaming: dict[Id, Id], ss: IList[src.Stmt]) -> IList[tgt.Stmt]:
    return IList([uniquify_stmt(renaming, s) for s in ss])

def uniquify_stmt(renaming: dict[Id, Id], s: src.Stmt) -> tgt.Stmt:
    match s:
        case src.SExpr(e):
            e = uniquify_expr(renaming, e)
            return tgt.SExpr(e)
        case src.SPrint(e):
            e = uniquify_expr(renaming, e)
            return tgt.SPrint(e)
        case src.SAssign(x, e):
            renamed_x = rename_variable(x, renaming)
            e = uniquify_expr(renaming, e)
            return tgt.SAssign(renamed_x, e)
        case src.SIf(e, b1, b2):
            e = uniquify_expr(renaming, e)
            b1 = uniquify_stmts(renaming, b1)
            b2 = uniquify_stmts(renaming, b2)
            return tgt.SIf(e, b1, b2)
        case src.SWhile(e, b):
            e = uniquify_expr(renaming, e)
            b = uniquify_stmts(renaming, b)
            return tgt.SWhile(e, b)
        case src.SReturn(e):
            e = uniquify_expr(renaming, e)
            return tgt.SReturn(e)

def rename_variable(variable: Id, renaming: dict[Id, Id]) -> Id:
    if variable not in renaming.keys():
        renaming[variable] = Id.fresh(variable.name)
    return renaming[variable]

def uniquify_expr(renaming: dict[Id, Id], e: src.Expr) -> tgt.Expr:
    match e:
        case src.EConst(c, size):
            return tgt.EConst(c, size)
        case src.EVar(x):
            return tgt.EVar(renaming[x])
        case src.EInput():
            return tgt.EInput()
        case src.EOp1(op, e1):
            e1 = uniquify_expr(renaming, e1)
            return tgt.EOp1(op, e1)
        case src.EOp2(e1, op, e2):
            e1 = uniquify_expr(renaming, e1)
            e2 = uniquify_expr(renaming, e2)
            return tgt.EOp2(e1, op, e2)
        case src.EIf(e1, e2, e3):
            e1 = uniquify_expr(renaming, e1)
            e2 = uniquify_expr(renaming, e2)
            e3 = uniquify_expr(renaming, e3)
            return tgt.EIf(e1, e2, e3)
        case src.ETupleAccess(e, i):
            return tgt.ETupleAccess(uniquify_expr(renaming, e), i)
        case src.ETupleLen(e):
            return tgt.ETupleLen(uniquify_expr(renaming, e))
        case src.ETuple(es):
            return tgt.ETuple(uniquify_exprs(renaming, es))
        case src.ECall(e_func, e_args):
            return tgt.ECall(uniquify_expr(renaming, e_func), uniquify_exprs(renaming, e_args))
        case src.ELambda(params, body):
            return uniquify_elambda(renaming, params, body)

def uniquify_exprs(renaming: dict[Id, Id], es: IList[src.Expr]) -> IList[tgt.Expr]:
    return IList([uniquify_expr(renaming, e) for e in es])
# END