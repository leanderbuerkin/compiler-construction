from dataclasses import dataclass
from typing import Any, Sequence
import ast

from ast_1_python import *
from identifier import Id
from util.immutable_list import IList

@dataclass(frozen=True)
class ParseError(Exception):
    pass

@dataclass(frozen=True)
class UnsupportedFeature(ParseError):
    node: Any

    def __str__(self) -> str:
        return f"Found unsupported AST node {self.node} that represents `{ast.unparse(self.node)}`\n\n `{ast.dump(self.node, indent=4)}`"

@dataclass(frozen=True)
class IllegalName(ParseError):
    name: str

    def __str__(self) -> str:
        return f"The `name` {self.name} is not a valid variable name, use only letters and numbers"

def map_node(node: ast.AST) -> Any:
    match node:
        case ast.Add():
            return "+"
        case ast.Sub() | ast.USub():
            return "-"
        case ast.Eq():
            return "=="
        case ast.NotEq():
            return "!="
        case ast.Lt():
            return "<"
        case ast.LtE():
            return "<="
        case ast.Gt():
            return ">"
        case ast.GtE():
            return ">="
        case ast.And():
            return "and"
        case ast.Or():
            return "or"
        case ast.Not():
            return "not"
        case ast.Constant(value) if type(value) is int or type(value) is bool:
            return EConst(value)
        case ast.Name(id, _):
            if not all([(c.isalnum() or c == "_") for c in id]):
                raise IllegalName(id)
            return EVar(Id(id))
        case ast.UnaryOp(op, operand):
            return EOp1(map_node(op), map_node(operand))
        case ast.BinOp(left, op, right) | ast.BoolOp(op, [left, right]) | ast.Compare(left, [op], [right]):
            return EOp2(map_node(left), map_node(op), map_node(right))
        case ast.If(test, body, orelse):
            return SIf(map_node(test), map_nodes(body), map_nodes(orelse))
        case ast.While(test, body, []):
            return SWhile(map_node(test), map_nodes(body))
        case ast.IfExp(test, body, orelse):
            return EIf(map_node(test), map_node(body), map_node(orelse))
        case ast.Assign([ast.Name(x)], value, _):
            return SAssign(Id(x), map_node(value))
        case ast.Call(ast.Name("input_int"), [], keywords) if len(keywords) == 0:
            return EInput()
        case ast.Expr(ast.Call(ast.Name("print"), [arg], keywords)) if len(keywords) == 0:
            return SPrint(map_node(arg))
        case ast.Expr(value):
            return SExpr(map_node(value))
        case _:
            raise UnsupportedFeature(node)

def map_nodes(nodes: Sequence[Any]) -> IList[Stmt]:
    return IList([map_node(node) for node in nodes])

def parse(src_str: str) -> Program:
    body: list[Any] = [] 
    for n in map_nodes(ast.parse(src_str).body):
        body += [n]
    return IList(body)
