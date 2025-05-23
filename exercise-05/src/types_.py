from dataclasses import dataclass
from util.immutable_list import IList

# Type Syntax
type Type = TInt | TBool | TTuple

@dataclass(frozen=True)
class TInt:
    pass

@dataclass(frozen=True)
class TBool:
    pass

@dataclass
class TTuple:
    ts: IList[Type]

# Pretty Printing
def pretty_type(t: Type) -> str:
    match t:
        case TInt():
            return "int"
        case TBool():
            return "bool"
        case TTuple(ts):
            return f"tuple[{pretty_types(ts)}]"

def pretty_types(ts: IList[Type]) -> str:
    return ", ".join(pretty_type(t) for t in ts)
