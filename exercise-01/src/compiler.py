from argparse import ArgumentParser
from sys import exit
from typing import Optional

import ast_1_python
import ast_2_mon
import ast_3_sel
import ast_4_mem
import ast_5_patched
import ast_6_riscv
from pass_0_1_parser import parse, ParseError
from pass_1_2_monadic import monadic
from pass_2_3_select import select
from pass_3_4_assign import assign_homes
from pass_4_5_patch import patch_instructions
from pass_5_6_prelude import add_prelude_and_conclusion
from type_checker import type_check, TypeError

# Read commandline arguments
arg_parser = ArgumentParser(
    prog="pycomp",
    description="Compiles a subset of Python to RISC-V assembly.",
)
arg_parser.add_argument(
    "-i", "--src", metavar="PATH", required=True, help="source file to compile"
)
arg_parser.add_argument(
    "-o",
    "--tgt",
    metavar="PATH",
    help="target file to save the assembly to (default: print to stdout)",
)
arg_parser.add_argument(
    "-v", "--verbose", action="store_true", help="debug print the output of all passes"
)
arg_parser.add_argument(
    "-V",
    "--very-verbose",
    action="store_true",
    help="debug print also the early parsing chart",
)
args = arg_parser.parse_args()

src_path: str = args.src
tgt_path: Optional[str] = args.tgt
verbose: bool = args.verbose
very_verbose: bool = args.very_verbose

if very_verbose:
    verbose = True

# Compilation
if verbose:
    print("\n===== READING SOURCE FILE =====\n")
try:
    with open(src_path, "r") as f:
        src_str = f.read()
except OSError as err:
    print(f"Failed reading from source file {src_path}: {err}")
    exit(1)
if verbose:
    print(src_str)

if verbose:
    print("\n===== PARSING =====\n")
try:
    ast = parse(src_str)
except ParseError as err:
    print(err)
    exit(1)
if verbose:
    print(f"{ast}\n\n{ast_1_python.pretty(ast)}")

if verbose:
    print("\n===== TYPE CHECKING =====\n")
try:
    type_check(ast)
except TypeError as err:
    print(err)
    exit(1)
if verbose:
    print("Program is well-typed.")

if verbose:
    print("\n===== MONADIC NORMALFORM =====\n")
ast = monadic(ast)
if verbose:
    print(ast_2_mon.pretty(ast))

if verbose:
    print("\n===== INSTRUCTION SELECTION =====\n")
ast = select(ast)
if verbose:
    print(ast_3_sel.pretty(ast))

if verbose:
    print("\n===== ASSIGN HOMES =====\n")
ast, offset = assign_homes(ast)
if verbose:
    print(ast_4_mem.pretty(ast))

if verbose:
    print("\n===== PATCH INSTRUCTIONS =====\n")
ast = patch_instructions(ast)
if verbose:
    print(ast_5_patched.pretty(ast))

if verbose:
    print("\n===== ADD PRELUDE & CONCLUSION =====\n")
ast = add_prelude_and_conclusion(ast, offset)
if verbose:
    print(ast_6_riscv.pretty(ast))

tgt_str = ast_6_riscv.pretty(ast)

if verbose:
    print("\n===== WRITING OUTPUT ASSEMBLY =====\n")
if tgt_path is None:
    print(tgt_str)
else:
    try:
        with open(tgt_path, "w+") as f:
            f.write(tgt_str)
    except OSError as err:
        print(f"Failed writing to target file {tgt_path}: {err}")
        exit(1)
    if verbose:
        print(f"Wrote output assembly to file {tgt_path}.")
