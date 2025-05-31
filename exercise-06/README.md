# Exercise 6

Your task is to extend the compiler for functions.

As always we already modified the interpreter, type checker, and syntax trees for you, so that you only have to extend the compiler passes.

The following is a description of the changes that have to be done to extend the compiler. Any change marked with a `TODO` will be your task to complete.

## AST

- `ast_1_python` is now extended with function definitions `DFun`,
  return statements `SReturn`, call expressions `ECall`,
  and a new constant `None` for functions that do not return a value.

- A program consists of a list of function declarations `decls` and a list of
  top-level statements `main_body`.

## Shrink

- In `pass_1_2_shrink` you need to compile the top-level statements
  into a `main` function, so the output program in `ast_2_shrunk` is
  now only a list of function declarations. This makes it a bit
  easier in the following passes, because you only need to handle
  functions. This also matches the output assembly, where instructions
  generated from the top-level statements make up the body of the
  `main` function.

## Reveal Functions

- `TODO:` In `pass_2_3_reveal_functions` you need to syntactically
  differentiate between regular variables, and variables that
  represent functions. A regular variable `EVar(x)` stays an
  `EVar(x)`, whereas a variable with a function name should become
  `EFunRef(x, arity)`, where `arity` is the number of parameters of
  the functions. The `arity` is not used in this exercise, but
  will become relevant when we add dynamic types later.

## Limit Functions

- `TODO:` In `pass_3_3_limit_functions` you need to convert functions (and function calls) with
  more than 8 arguments to functions with 8 arguments, where the last
  argument is a tuple of the rest of the arguments. This is necessary
  starting from argument 9 we don't have argument registers anymore,
  so the arguments need to be passed on the stack, but passing
  arguments on the stack makes tail call optimization more tricky.
  
- This pass is separate from `pass_2_3_reveal_functions`, because in
  the next exercise there will be new passes in between those two.

## Alloc

- In `pass_3_4_alloc` nothing interesting happens, as this pass only
  affects `ETuple` expressions.

## Monadic

- In `pass_4_5_monadic` nothing interesting happens. Call expressions and FunRefs
  are non-atomic and return statements are allowed to contain
  non-atomic expressions. This is necessary for tail-call
  optimization, where we need to be able to detect when the result of
  a function call is returned.

## Explicate

- In `pass_5_6_explicate` the body of each function needs to be
  replaced with the basic blocks resulting from explicating the
  body. The output function definition `tgt.DFun` contains fields
  `start_label` and `end_label`, to track which blocks are the entry
  and exit blocks to the function, and which blocks are internal
  (e.g. from an `if`-statement).
  We use the following block layout for a function `f`:
  ```
  f:
      HERE WE WILL LATER INSERT THE PRELUDE
      j f_start

  f_start:
      INSTRUCTIONS OF THE FUNCTION BODY
  
  POTENTIALLY MORE BLOCKS OF THE FUNCTION BODY
  
  f_conclusion:
      HERE WE WILL LATER INSERT THE CONCLUSION
  ```
  At this point, you should create blocks for `f`, `f_start` and all
  the internal blocks, but not yet the block `f_conclusion` as an
  empty block without a jump, would confuse register allocation.
  
- `TODO:` Furthermore, this pass should reveal tailcalls, i.e. if a return
  statement contains a call as a direct subexpression, then it should
  be translated to a special tail call statement `STailCall`,
  otherwise it stays a return statement, but with the subexpression assigned to
  and replaced by a new temporary variable.
## Select

- `TODO:` In `pass_6_7_select` you need to remove the parameters from function
  definitions and instead insert assignments from the argument
  registers to the parameters at the beginning of the function.
  
- Assignments of function references `EFunRef` simply use the function
  label as the value.
  
- `TODO:` Assignments of call expressions `ECall` move their arguments in the
  argument registers (you may use the `FUNCTION_ARG_REGISTERS` variable from
  `register.py`), call the function, and move the result register
  to the lhs of the assignment. Tail calls `STailCall` work similar to calls,
  but leave the result in the result register.
  
  To differentiate between the different kinds of calls, `tgt.Call` is
  defined as follows:
  ```python
  @dataclass(frozen=True)
  class Call:
      target: ArgRead                    # address of the function
      arity: int                         # the arity (number of params) of the function
      ty: Literal['normal', 'tail call'] # whether to do a tail-call or not
  ```
 
- `TODO:` Assignments of return statements `SReturn`, move their argument to
  the return register and jump to the functions conclusion label.
  
- The `ast_7_sel` was refactored to allow more instruction arguments.
  At most places now `ReadArg` and `WriteArg` are used which specify
  the type of arguments for destination and source arguments in
  instructions. This allows for a bit more flexibility in the
  instruction selection pass and a bit more of patching in the patch
  instructions pass.

## Assign Homes

- In `register_allocation` registers need to be allocated for each
  function individually.  Hence, it returns a dictionary from function
  labels to `RegAllocOutput` instead of just a single
  `RegAllocOutput`.
  
- Furthermore, care needs to be taken, that all calls to user
  functions potentially trigger garbage collection, so `gc_collect` is
  not the only function for which live variables need to be spilled to
  the stack.

- In `pass_7_8_assign_homes` the `assign_homes` function now needs to
  take a dictionary which maps function labels to register allocator
  output, as register allocation needs to be run for each function
  individually.

## Patch Instructions

- In `pass_8_9_patch_instructions` the different kinds of `Call`
  instructions need to be translated to the corresponding RISC-V
  instructions.
  
- This pass now doesn't produce RISC-V assembly, but instead
  `ast_9_patched` programs. Those are identical to RISC-V assembly,
  but have a notion of functions and have two more instructions
  `TailJump` and `TailJumpIndirect` (for tail calls via labels and tail jumps via registers, respectively).
  Those are necessary, because tail calls require their own conclusion and it makes more sense to
  generate conclusions consistently in the next pass, where we also
  generate the normal prelude and conclusion.

## Add Prelude

- In `pass_9_10_add_prelude` we need to generate appropriate preludes
  and conclusions for each function.

- The `main` function requires special treatment, as it initializes
  the garbage collector and always returns 0.
  
- `TODO:` The `TailJump` and `TailJumpIndirect` calls need to be compiled away
  by replacing them with appropriate conclusions (you should use the `compute_conclusion` function for that)
  followed by an indirect jump to the target function, using the `IndirectJump` instruction.
  
- A tail call conclusion differs from a regular conclusion by
  jumping instead of using `ret`.

- The `.globl LABEL` and `.align 8` assembly directives should be
  inserted before each function label to make sure the function is
  exposed by the linker and that the function addresses are aligned by
  8 bytes.

- To make adding labels easier, we refactored the `ast_10_riscv`
  syntax tree. It is now simply a list of instructions and we count
  labels and assembly directives also as instructions, i.e. each
  `Instr` corresponds to exactly one line in the output assembly.

- Our function definitions `DFun` carry around the parameter and
  return types. Those are intended to remain unused in this
  exercise, but they may become relevant in later exercises.

If stuff is unclear, don't hesitate to use the chat!

*Happy Coding! <3*