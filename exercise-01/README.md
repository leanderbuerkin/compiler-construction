# Exercise 1

In this exercise, your task is to implement a complete compiler for
the `Lvar` language from Chapter 2 to RISC-V assembly. This exercise
is based on the exercises from Chapter 2 with slight modifications and
a more sane starter codebase (in particular no OOP nonsense).

The directory structure is as follows:

-   `runtime/runtime.c` contains the runtime for our language written in C.
    This includes in particular the `print_int64` and `input_int64`
    functions, which are called by the assembly code resulting from
    `input_int()` expressions and `print_int(e)` statements.
    
-   The `src/` directory contains the python code for the interpreter
    and compiler:
  
    -   the modules `ast_1_python`, `ast_2_mon`, `ast_3_var`,
        `ast_4_mem`, `ast_5_patched`, `ast_6_riscv`, and `register` contain data type
        definitions for the abstract syntax trees of our source
        language, target language and the intermediate representations (IR).

    -   the modules starting with `pass_*` contain the individual
        compiler and interpreter passes translating between the
        different data representations, e.g. `pass_1_2_monadic` contains
        the conversion from the `Lvar` syntax tree from `ast_1_python`
        to the intermediate representation in monadic normal form from
        `ast_2_mon`.

    -   the `interpreter.py` is the entry point for an interpreter of
        the `Lvar` language.  This interpreter can be use as a
        reference, i.e. if you compile and run a `Lvar` program it
        should have the same behavior as if you interpret it. Our test
        script in `tests/test.py` automates exactly this process.

    -   the `compiler.py` is the entry point for your compiler of
        `Lvar` language.

    -   the `util/` directory contains library code relevant for the
        compiler:

        -   in `immutable_list.py` you find an implementation of
            covariant immutable lists. They are used in
            `parser.py`, but also in the syntax trees, where
            covariance is necessary for the pylance/pyright or mypy type
            checker to do proper type inference.

-   The `tests/` directory contains a testing framework for
    `src/compiler.py`. The `tests/test.py` file takes each file in
    `tests/**/`, e.g. `test/01/add-2.py` and compares the output of running
    it with `src/interpreter.py` vs the output of compiling it with
    `src/compiler.py`, linking it together with the runtime and
    running it with `qemu`.
    The `test.py` file is intended to be run from within the
    docker image from `Dockerfile`. See documentation of the `do`-script below.

-   The `do` script is a helper utility for running the compiler and
    tests inside of the docker image that provides the RISC-V cross
    compilation toolchain.
    
    The most important commands are:

    - `./do shell`, which drops you into an interactive shell inside
      of the docker container with the project directory mounted.
      This means you can work in there, like you would from a local terminal,
      but have the RISC-V `gcc` and `qemu` programs available.
      For example, you can run the tests by running `python3.12
      tests/tests.py` inside this shell.

    - `./do test` runs `tests/tests.py` in the docker container.

    - `./do run source.py -v` runs `python3.12 compiler.py source.py -v`,
      compiles the output with RISC-V `gcc` and runs it with `qemu`.
      This is useful for debugging a failing test-case.
      
    - For more details check out `./do --help`

## Tasks

Your tasks are to implement the missing compiler passes. In particular:

1.  Make yourself familiar with the existing code base by reading
    through the source files and matching the code to the concepts
    you've learned in the lectures. A good starting point is the
    `src/compiler.py` file, which is the entry point for the compiler.

2.  In `src/pass_1_2_monadic.py` you should implement a transformation
    from the `Lvar` abstract syntax tree `ast_1_python` to monadic
    normal form `ast_2_mon` as demonstrated in the lectures and
    Chapter 2.

3.  In `src/pass_2_3_select.py` you should implement instruction
    selection, i.e. a transformation from the monadic normalform
    `ast_2_mon` to `ast_3_sel` as demonstrated in the lectures and
    Chapter 2.

4.  In `src/pass_3_4_assign.py` you should implement a simple
    register allocation, i.e. the `assign_homes` functions which
    transform an `ast_3_sel` to an `ast_4_mem` syntax tree as
    demonstrated in the lectures and Chapter 2.

5.  In `src/pass_patch.py` you should implement the
    `patch_instructions` function to transform the `ast_4_mem` syntax
    tree to an `ast_5_patched` syntax tree (for now this is the same as `ast_6_riscv`),
    as demonstrated in the lectures and Chapter 2.

6.  In `src/pass_prelude.py` you should transform the patched RISC-V
    assembly to RISC-V assembly by adding a prelude and conclusion to
    make it a complete program as demonstrated in the lectures and Chapter 2.

## General hints

- Compilers and interpreters have a lot of tree transformations.
  Using pattern matching all over the place tends to greatly improve
  code readability.

- We recommend using the pylance/pyright or mypy typechecker to catch errors
  and remind you when you forget cases in your pattern matching.
  We have written the codebase in a way that it even works if
  pylance/pyright is set to `strict` mode (e.g. with vscode and the
  standard python extension, you can set this in the vscode options),
  however `strict` mode requires you at a few places to jump through a
  few hoops to make the type checker happy. Feel free to ask in the chat
  if you hit those cases. Otherwise, using the non-strict type-checking
  mode also already provides you with many benefits (in particular
  pattern matching exhaustiveness checks, if you use type
  annotations).

Happy Coding! <3
