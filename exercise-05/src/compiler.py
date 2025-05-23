from argparse import ArgumentParser
from sys import exit
from typing import Any, Optional

import ast_1_python
import ast_2_shrunk
import ast_3_alloc
import ast_4_mon
import ast_5_exp
import ast_6_sel
import ast_7_mem
import ast_8_patched
import ast_9_riscv
from pass_0_1_parser import parse, ParseError
from pass_1_2_shrink import shrink
from pass_2_3_alloc import alloc
from pass_3_4_monadic import monadic
from pass_4_5_explicate import explicate
from pass_5_6_select import select
from pass_6_7_assign import assign_homes
from pass_7_8_patch import patch_instructions
from pass_8_9_prelude import add_prelude_and_conclusion
from register_allocation import allocate_registers
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

ast: Any

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
    print("\n===== SHRINKING =====\n")
ast = shrink(ast)
if verbose:
    print(ast_2_shrunk.pretty(ast))

if verbose:
    print("\n===== HEAP ALLOCATION =====\n")
ast = alloc(ast)
if verbose:
    print(ast_3_alloc.pretty(ast))

if verbose:
    print("\n===== MONADIC NORMALFORM =====\n")
ast = monadic(ast)
if verbose:
    print(ast_4_mon.pretty(ast))

if verbose:
    print("\n===== EXPLICATE CONTROL =====\n")
ast = explicate(ast)
if verbose:
    print(ast_5_exp.pretty(ast))

if verbose:
    print("\n===== INSTRUCTION SELECTION =====\n")
ast = select(ast)
if verbose:
    print(ast_6_sel.pretty(ast))

if verbose:
    print("\n===== REGISTER ALLOCATION =====\n")
reg_alloc = allocate_registers(ast)
if verbose:
    for key, val in reg_alloc.env.items():
        print(f"\t{key}: {val}")

if verbose:
    print("\n===== ASSIGN HOMES =====\n")
ast = assign_homes(ast, reg_alloc)
if verbose:
    print(ast_7_mem.pretty(ast))

if verbose:
    print("\n===== PATCH INSTRUCTIONS =====\n")
ast = patch_instructions(ast)
if verbose:
    print(ast_8_patched.pretty(ast))

if verbose:
    print("\n===== ADD PRELUDE & CONCLUSION =====\n")
ast = add_prelude_and_conclusion(ast, reg_alloc)
if verbose:
    print(ast_9_riscv.pretty(ast))

tgt_str = ast_9_riscv.pretty(ast)

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
