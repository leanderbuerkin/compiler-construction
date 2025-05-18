from dataclasses import dataclass
from util.immutable_list import IList

# Type Syntax
type Type = TInt | TBool

@dataclass(frozen=True)
class TInt:
    pass

@dataclass(frozen=True)
class TBool:
    pass

# Pretty Printing
def pretty_type(t: Type) -> str:
    match t:
        case TInt():
            return "int"
        case TBool():
            return "bool"

def pretty_types(ts: IList[Type]) -> str:
    return ", ".join(pretty_type(t) for t in ts)
