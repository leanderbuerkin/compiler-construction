# Exercise 7

Your task is to extend the compiler for lexically scoped functions, i.e. lambda expressions.

As always we already modified the interpreter, type checker, and syntax trees for you, so that you only have to extend the compiler passes.

The following is a description of the non-trivial changes that have to be done to extend the compiler. Any change marked with a `TODO` will be your task to complete.

## AST

- We decided to not cover dynamic and gradual types, so we can simplify
  our a implementation a bit compared to the book, where they already
  introduce some constructs with dynamic typing in mind.
  
  In particular:
  - we do not need the arity in a function reference `EFunRef`
  - we do not need an expression to tell us the arity of a function
  - we do not need types in the intermediate language, so we remove them
    in `pass_1_2_shrink` from function definitions `DFun`
  - we do not need to separate between a tuple `ETuple` and a closure.
    In the book a closure is like a tuple but has an extra arity.
  - we do not need to separate between tuple allocation `EAlloc` and
    closure allocation, because closures *are* now tuples.

- `ast_1_python` is now extended with anonymous function expressions
  `ELambda` and `SAssign` carries an optional type annotation.
  This type annotation is only needed for type checking, and is removed
  in the shrinking pass.

## Uniquify

- `TODO:` We need a new `pass_2_2_uniquify`, which renames all variables to
  have unique names. Make sure that parameters of a lambda expression shadow variables
  with the same name from the outside.

## Convert Assignments

- `TODO:` We need a new `pass_3_4_convert_assignments`, which makes sure that
  our lambdas treat captured variables as the lambdas in Python would
  do. Consider for example:
  ```python
  x = 1
  y = 1
  f = lambda x: x + y
  y = 10
  print(f(1))
  ```
  This program will print `11`, because the integer value in `y` is
  not copied into the lambda, but instead a pointer to `y` is copied
  there.
  
  First we need to analyse the program to find such variables, i.e.
  variables which are free in lambda expressions and which are
  assigned to.
  
  Second we need to box those variables, by replacing them with one-tuples.
  For example, for the above program we would want an intermediary program
  which vaguely looks as follows:

  ```python
  y = (0,)  # initialize to 0
  x = 1
  y[0] = 1
  f = lambda x: x + y[0]
  y[0] = 10
  print(f(1))
  ```
  
  Make sure to handle the initial value of boxed variables correctly, because boxed
  variables can also be parameters of the function in which they are used.

  We also annotate each lambda expression with its captured variables, because
  we need them in the next pass again.

## Closure Conversion

- `TODO:` We need a new `pass_4_5_closure_conversion`, which creates for
  each lambda a regular function definition, and replaces the lambda
  by a closure, i.e. a tuple containing a function pointer and the
  values of the variables captured by the lambda.
  
  To allow top-level functions and functions resulting from lambdas
  to be treated in the same way, we also create closures for
  references to top-level functions. As they don't capture anything,
  their closures contain only the function references itself.
  
  All functions need to take a new first argument - the closure - and need
  to define the free variables based on the content of the closure.
  For example, for the above program we would want an intermediary program
  which vaguely looks as follows

  ```python

  def lambda(closure, x):
    y = closure[1]
    return x + y[0]

  y = (0,)
  x = 1
  y[0] = 1
  f = (lambda, y)
  y[0] = 10
  print(f[0](f, 1))
  ```
  
  `ast_5_closures` supports begin expression to properly handle function calls.

## 
  
- At this point everything that came from the lambda has been encoded
  as tuples and indirect calls to function pointers, which we can
  already handle since the previous exercises, so the rest of the
  compiler passes stay the same.

- We fixed a bug related to register allocation and value tagging.
  The content of the callee-saved registers of the main function contains
  untagged values from whoever calls main. For this purpose we already
  tell the garbage collector to not start at the stack-pointer at the
  beginning of the main-function, but after the stack-locations of
  spilled callee-saved registers.

  However, now that we have functions, it could happen that the main
  function does not spill the callee-saved registers, but another
  function called by main does, which would then lead to untagged
  values in the middle of the stack.  To prevent this, register
  allocation and the prelude and conclusion have been adjusted, such
  that all callee-saved registers of the main function are spilled,
  and that the callee-saved registers are then subsequently
  overwritten with zero in the prelude, such that when another
  function spills the callee-saved registers, no untagged values are
  written to the stack.

If stuff is unclear, don't hesitate to use the chat!

*Happy Coding! <3*