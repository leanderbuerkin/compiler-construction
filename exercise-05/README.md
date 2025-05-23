# Exercise 5

In this exercise, your task is to extend the compiler with
tuples, which are heap-allocated via a garbage collector.

## Task

As always, we already extended the parser and syntax trees, but
leave the extension of the passes to you.

The following highlights the changes we did to the code and some of
the key challenges of the exercise (but we again marked the places in the code, where you need to insert logic yourself with `...` or `# TODO`):

-   We provide an implementation of a garbage collector, as described in the
    lecture, in the `runtime/runtime.c`. The API of this garbage
    collector is also presented in this file and separated from the
    implementation, so check it out :)
    
    The garbage collector can be compiled in debugging mode to
    print verbose information about what it is collecting when.
    For this purpose you need to pass the additional command line argument
    `-D DEBUG` to `gcc` when you are compiling and linking the runtime
    together with the assembly output of the compiler, or alternatively
    add a `#define DEBUG` at the top of the `runtime.c` file.
    Note, that you need to remove this `#define DEBUG` again, if you are
    running the testcases, because it changes the output of the program
    and makes it incomparable to the output of the interpreted program.

-   The python AST `ast_1_python` has 3 new nodes and 1 new operator:
    - `ETuple` represents a tuple expression, e.g. `(1, True, 2)`
    - `ETupleAccess` represents a tuple subscript, e.g. `t[0]`
    - `ETupleLen` represents the tuple length function, e.g. `len(t)`
    - `"is"` is the binary operator to check if two tuples are the
      *same*, e.g. `t1 is t2`

-   The type checker allows `is` only for tuples, and `==` only for
    non-tuples, i.e. we have `t1 is t2` to check if the tuples as the
    *same* tuple, but no `t1 == t2` to check if both tuples are equal.
    The meaning of `is` and `==` is consistent with the meaning of
    those operations in Python.

-   The shrinking pass `pass_1_2_shrink` needs to replace the `"is"`
    operator with `"=="`, as in our intermediate languages `"=="`
    means to directly compare the values, i.e. to check if the
    pointers of both tuples are the same, and not the data behind the
    pointers.

    If we would also support the `==`-operator on tuples as in python,
    then the shrink pass would additionally translate python's `==` to
    a function call instead, that checks equality of the *data*
    contained in the tuples.
    
    The shrinking pass additionally needs to translate constants to
    help with value tagging.
    
    Recall that, constants in our surface language (`ast_1_python`)
    should be translated to 63bit integers, because we use the last
    bit of any 64bit value as a tag, which says if the value is a heap
    pointer or not (see slides about value tagging).
    Consequently, at some point in the compiler we need to translate
    the constants written in the user code to 63bit integers by
    multiplying them by two. 
    
    We could multiply all integer constants directly, but then
    debug printing the syntax trees of the intermediate languages
    would look confusing, e.g. if the user wrote `x = 3`, it would
    print `x = 6`.

    To enable better debug printing, and also avoid confusion in the
    compiler passes, we distinguish between the two representations
    syntactically, e.g.  we have `EConst(3, '64bit')` and
    `EConst(3, '63bit')`, where the former represents 64bit number `3`
    and the latter represents the 64bit number `6`.
    
    This allows nice debug printing, e.g. the former is printed as
    `3°` and the latter as `6`, where the `°` symbolizes that we take
    the binary representation of `3` and put a `0` at the right of it.
    
    We use these kinds of constants for all syntax trees from
    `ast_2_shrunk` to `ast_7_mem`, such that we can still recognize
    the numbers written in the input code, and to force ourselves to
    think how we want to represent constants if we introduce new ones
    in the compiler passes.
    
    The idea is to compile all constants `EConst(x)` from user code to
    `EConst(x, '63bit')` as early as possible (i.e. in the shrinking
    pass), and compile them away as late as possible (i.e. in
    `patch_instructions`), where `EConst(x, '64bit')` will be just
    `x`, but `EConst(x, '63bit')` will be `x * 2`.

-   After the shrinking pass, we need a new pass `pass_2_3_alloc`. The
    sole purpose of this pass is to expand tuple literals, e.g. 
    `(1, True, 2)`, to code which actually performs the allocation
    by interacting with the garbage collector API.

    As the expanded code involves `if`-statements, it is easier to do
    this expansion relatively early in the compilation pipeline,
    because then one doesn't need to write the expanded code in
    monadic normal form or even by using basic blocks and jumps.
    
    The target language of this pass `ast_3_alloc` contains
    -   global variables `EGlobal`, which stand for the value of a
        global variable (and not its address)
    -   garbage collection statements `SCollect(requested_words)`,
        which stand for running the garbage collector by calling
        `gc_collect`.
    -   allocation expressions `EAlloc(num_words)`, which stand
        for allocating heap space of size `num_words + 1`
        and assume that enough heap space is available.
        The `+ 1` is for the garbage collection meta information
        stored in the first word of the allocated space, which this
        expression also fills in.
    -   an expression `EBegin(stmts, expr)`, which stands for first
        running the statements `stmts` and then evaluating the
        expression `expr`.
    -   a second form of assignment statements with subscripts on the
        left-hand-side, e.g. `x[0] = e`. Those are required to
        initialize the tuple entries after memory allocation.
        
    Those constructs need to be put together such that first it is
    checked if the from-space of the garbage collector still has
    enough free memory.  If this is not the case, the garbage
    collection needs to be run.  Afterwards, the allocation can be
    performed, because if the program is still running, then the
    garbage collector succeeded in freeing enough memory by copying
    and potentially also increasing its from- and to-spaces.
    
    As an `ETuple` expression might appear somewhere in the condition
    of a `while`-loop, all statements resulting from the expansion
    need to be placed in an `EBegin` expression, such that they are
    not only run initially, but for each iteration of the
    `while`-loop.
    
    We postpone expanding `EAlloc` and `SCollect` further until
    we reach a point in the compilation pipeline, where we can express
    pointer dereferenciation.

-   In `pass_3_4_monadic`, we need to deal with the new constructs
    introduced in the previous pass.
    
    We consider `EGlobal` as complex expressions, because they will
    compile to a pointer dereferenciation.
    
    We translate the `EBegin(stmts, expr)` by simply translating
    `stmts` and `expr` in sequence.  The `SWhile` statement itself is
    responsible for collecting all statements, which resulted from its
    condition expression and storing it in the output `SWhile`
    statement.
    
    The other constructs work similar as in previous exercises.
        
-   In pass `pass_4_5_explicate`, the new constructs work similar as
    in the previous exercises.

-   In pass `pass_5_6_select` the following cases are relevant:

    -   `EGlobal` expressions are translated to actually accessing the
        global variable via an Offset. For this purpose `Offset` now
        also supports taking the offset of a `Label`.
        
    -   `SCollect` statements need to be translated to a function call
        to `gc_collect` from `runtime/runtime.c` with appropriately
        set argument registers `a0` and `a1`.
        
    -   Assignments with `EAlloc` expressions on the right-hand-side
        use the pointer in `gc_free_ptr` as the pointer to the
        allocated memory, adjust the `gc_free_ptr` according to how
        much memory was used, and set the first word of the allocated
        memory to contain the meta information for the garbage
        collector.
        
        Care needs to be taken to also tag the pointer retrieved from
        `gc_free_ptr` as a heap pointer.
        
    -   Assignments with `ETupleLen` expressions on the
        right-hand-side need to retrieve the garbage collection meta
        data and extract the length of the tuple from it.
        
        Care needs to be taken to think about value tagging of the
        computed length (1 if it is a heap pointer) and the tagging
        used in the meta data itself (1 if it is currently copied,
        which only happens *during* garbage collection)
        
    -   Assignments with `ETupleAccess` expressions on the
        right-hand-side need to retrieve the corresponding entry value
        from the heap allocation.
        
    -   Print and input statements need to take care that in our
        language we use 63bit integers, but the C functions
        `print_int64` and `input_int64` do not.

    -   Some of the operators need to be adjusted to work with value
        tagging.
    
        Additionally to the cases mentioned in the slides, the "set
        if" instructions, like `sltu`, also require special care.
        Those are produced for assignments, where the right-hand-side
        is a comparison operator, and produce untagged booleans as
        output, whereas we require tagged booleans as output.
        
    -   Assignments can now also contain subscripts on the
        left-hand-side (which we used to initialize tuple entries),
        which corresponds to using `Offset`s as destinations in the
        output instructions.

-   The `register_allocation` needs to make sure that calls to
    `gc_collect` are treated specially: they cause all live variables
    to interfere with all registers.  This makes sure that before
    garbage collection all live variables are spilled to the stack,
    such that the garbage collector can change the addresses of tuples
    to their new locations.

    Furthermore, the read and write sets now also need to deal with
    globals and offsets.

-   In pass `pass_6_7_assign_homes` we need to add cases because we
    now also allow `Offset`s and `Label`s in our instructions.
    
    As we already require `Offset`s in earlier passes,
    e.g. `-7(tuple)` where tuple is a temporary, it can happen that
    the garbage collector decides to spill `tuple` to the stack and
    replaces it, with `-7(-48(fp))`. We decided to allow such nested
    offsets and get rid of them in `pass_7_8_patch_instructions`.

-   In pass `pass_7_8_patch_instructinos`, we need to take care of the
    following cases:

    -   We have new instructions for shifting (`sll` and `srl`) and
        mutliplication and division (`mul` and `div`).
        The shifting instructions have immediate forms (`slli` and
        `srli`), but multiplication and division do not, so for the
        latter we always need to put constant arguments in registers
        first.
        
    -   Source and destination arguments of the instructions can now
        additionally contain labels (addresses of global variables)
        and nested offsets.

        RISC-V does not allow labels in offsets, so labels need to
        be loaded in a separate register first with the load address
        (`la`) instruction.
        
        Nested offsets as source arguments, e.g. `add s5, s6, -8(-32(s7))`
        can be implemented as multiple loads, where the same register
        can be used to store the result, e.g.
        ```
        ld a1, -32(s7)
        ld a1, -8(a1)
        add s5, s6, a1
        ```
        
        Nested offsets as destination arguments can be implemented as
        multiple loads followed by a single store.
        
        We recommend writing two functions `patch_load_offset` and
        `patch_store_offset` for this purpose, where the former is
        recursive and the latter calls the former.
        
    -   Constants need to be expanded depending on whether they are
        63bit or 64bit constants as described above
    
-   In `pass_add_prelude` we need to make sure to initialize the
    garbage collector by calling `gc_init`.

    `gc_init` takes a pointer to the begin of the stack and the
    initial size in words for the from- and to-space.
    
    There are two subtle things that need to be taken care of:
    
    1.  We cannot simply use the begin of the stack (`sp`) for
        `gc_init`, because at the beginning of the `main` function, we
        need to store the callee-saved registers, which contain
        untagged values which might end with a `1`, so our garbage
        collector would think that it's a heap pointer and crash.
        Instead we call `gc_init` with a pointer to the first element
        on the stack that comes *after* the callee-saved registers in
        `main`.
        
    2.  At the beginning of the main function we increase the stack
        pointer by the size of the whole stack frame.  However, the
        memory only get's gradually initialized while the instructions
        in the function execute.  This means if we call `gc_collect`
        with the current stack pointer, then the garbage collector
        will try to inspect also those stack locations that have not
        yet been initialized, and would yield undefined behavior or
        crash if the uninitialized memory happens to have a 1 in the
        "is-heap-pointer" tag.

        There are two ways to prevent this:

        1.  We dynamically increase the stack-pointer after we
            initialize the corresponding stack location.

        2.  We increase the stack-pointer as before only at the
            beginning of the function, but afterwards initialize all
            the stack locations with zeros.
            
        We take the second approach, as it is simpler. Setting the
        stack locations to zero, can be done by simply producing a
        store instruction reading from the `zero` register for each
        stack location.

Happy Coding! <3

