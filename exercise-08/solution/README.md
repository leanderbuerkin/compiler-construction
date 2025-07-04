# Exercise 8

Your task is to extend the compiler with simple (data-) classes.

As always we already modified the interpreter, type checker, and syntax trees for you, so that you only have to extend the compiler passes.

The following is a description of the non-trivial changes that have to be done to extend the compiler. Any change marked with a `TODO` will be your task to complete.

## AST

`ast_1_python` is now extended with field access expressions
`EField` and `SClass` declares a new (data-) class:

```py
@dataclass
class EField:
    e: Expr
    name: Id
    idx: int | None = None  # set during type checking:
                            # indicates the position of this field in the class

@dataclass(frozen=True)
class SClass:
    name: Id
    fields: IList[tuple[Id, Type]]
```

The top-level structure of a program now needs to preserve the order of declarations and statements:

```py
@dataclass
class Program:
    body: IList[Decl | Stmt]
```

## Shrink

`TODO:` (Data-) classes are essentially syntactic sugar for tuples,
so we can "compile them away" completely in the shrink pass.

A dataclass definition `SClass(name, [f₁, ..., fₙ])` on the toplevel should
be translated to a function definition

```py
def name (f₁, ..., fₙ):
  return (f₁, ..., fₙ)
```

If the class is defined *inside* a function definition it needs to be 
translated to a lambda expression:

```py
name = lambda f₁, ..., fₙ: (f₁, ..., fₙ)
```

Finally, the work for a field access expression `EField(e, field, idx)` was already 
done by the type checker: the `idx` contains the position of the `field` in the tuple `e`.
Thus, we translate it as follows:

```py
e[idx]
```

##

At this point everything that came from the (data-) classes has been encoded
as functions, lambdas or tuples, which we can
already handle since the previous exercises, so the rest of the
compiler passes stay the same.

As you can see, we are now able to build upon our existing features to integrate more advanced features easily.

Next time, we will move from the high level of the compiler back to the low level and look at peep-hole optimizations for our generated assembly code.

If stuff is unclear, don't hesitate to use the chat!

*Happy Coding! <3*
