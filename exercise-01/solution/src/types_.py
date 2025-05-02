from dataclasses import dataclass
from util.immutable_list import IList

# Type Syntax
type Type = TInt

@dataclass
class TInt:
    pass


# Pretty Printing
def pretty_type(t: Type) -> str:
    match t:
        case TInt():
            return "int"

def pretty_types(ts: IList[Type]) -> str:
    return ", ".join(pretty_type(t) for t in ts)
