# Exercise 3

In this exercise, your task is to implement a complete compiler for
the Lif language from Chapter 5 to RISC-V assembly. This exercise
is based on the exercises from chapter 5 with slight modifications and
a simpler starter codebase.

The additions/changes to the template are as follows:
    
- `src/`:   
    - `util/directed_graph.py`:  added simple directed graph implementation
    - `ast_1_python.py`: added language constructs introduced with Lif  
    - `ast_2_shrunk.py`: added target ast for `pass_1_2_shrink`
    - `ast_3_mon.py`: added language constructs introduced with Lif
    - `ast_4_exp.py`: added target ast for `pass_3_4_explicate`  
    - `ast_5_sel.py`: added language constructs introduced with Lif 
    - `ast_6_mem.py`: added language constructs introduced with Lif
    - `ast_7_mem.py`: added language constructs introduced with Lif
    - `ast_8_riscv.py`: added language constructs introduced with Lif
    - `compiler.py`: added calls to the new passes
    - `pass_0_1_parser.py`: added adapter to python standard library ast and parser
    - `pass_1_2_shrink.py`: added template for explicate control pass **[you need to implement this part!]**
    - `pass_2_3_monadic.py`: added support for Lvar **[you need to implement the Lif part!]**
    - `pass_3_4_explicate.py`: added template for explicate control pass **[you need to implement this part!]**
    - `pass_4_5_select.py`: added support for Lvar and handling of blocks **[you need to implement the Lif part!]**
    - `pass_5_6_assign.py`: added handling of blocks
    - `pass_6_7_patch.py`: added support for Lvar **[you need to implement the Lif part!]**
    - `pass_7_8_prelude.py`: added handling of blocks
    - `type_checker.py`: added support for language constructs introduced with Lif
    - `semantics.py`: added support for language constructs introduced with Lif
    - `register_allocation.py`: added support for Lvar **[you need to implement the Lif part!]**

## Tasks

Your task is to implement `pass_1_2_shrink` and `pass_3_4_explicate` as well as to modify the `pass_2_3_monadic`, `pass_4_5_select`, `register_allocation` and `pass_6_7_patch`. 
Look at the list above and implement the missing pieces (search for `...` inside the files).

Happy Coding! <3
