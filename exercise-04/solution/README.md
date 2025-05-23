# Exercise 4

In this exercise, your task is to extend the compiler with
`while` loops.

As always, we already extended the parser and syntax trees, but
leave the extension of the passes to you.

The following highlights the changes we did to the code and some of
the key challenges of the exercise:

-   The python AST is changed only through adding a while statement:

    ```python
    @dataclass(frozen=True)
    class SWhile:
        test: Expr
        body: IList[Stmt]
    ```

-   In `pass_1_2_shrink` nothing exciting happens, and you can treat the
    `while` similar to an `if`.

-   In `pass_2_3_monadic` you need to take special care to keep the
    statements generated from the `while` condition expression
    separate from the statements surrounding the while. For this
    purpose, the `while` in `ast_3_mon` is modelled as

    ```python
    @dataclass(frozen=True)
    class SWhile:
        test_body: IList[Stmt]
        test_expr: ECompare
        loop_body: IList[Stmt]
    ```

    where `test_body` and `text_expr` represent *both* the statements and
    the expression resulting from translating the condition expression
    into monadic normal form.

    This is necessary, because the condition of the `while` needs to be
    reevaluated in each iteration of the loop, so the `pass_3_4_explicate` needs
    to know which statements belong to the condition and which statements
    come from before the `while` loop.

-   In `pass_3_4_explicate` you need to translate the `while` loop to
    basic blocks. The easiest way to do this is to use separate
    basic blocks for `test_body`, `test_expr`, and `loop_body`. Once
    you figured out what basic blocks exactly to generate and how to
    link them, explicating a `while` is very similar to explicating an
    `if`.
    
-   In `pass_4_5_select` nothing needs to be changed, as the `pass_explicate` has translated
    the `while` to the same primitives as an `if`. 
    Similarly `pass_5_6_assign`, `pass_6_7_patch` and `pass_7_8_prelude` do not need to be changed.

-   In `register_allocation` you need to significantly refactor and
    extend the code. This is because `while` statements lead to
    *cyclic* control flow graphs, and consequently liveness cannot be
    computed by traversing the graph in a topological ordering, but a
    fixpoint computation is necessary via a dataflow analysis.
    
    We recommend dividing the `allocate_registers` function into 5 subfunctions:

    -   A function `control_flow_graph`, which builds a control flow graph from a program.
        This works the same as in the previous exercise. 

    -   A function `liveness_analysis`, which given a program and a
        control flow graph computes the liveness information for all
        instructions of all basic blocks.  We recommend basing this
        function on the generic data flow algorithm presented in
        Figure 6.5 on page 94 of the book, but specializing and
        modifying it to our needs.
        In particular, the algorithm from the book applies an external
        `transfer` function to entire basic blocks, so the `mapping`
        variable would store only a single live set for each basic
        block instead of live sets for each instruction.

    -   A function `interference_graph`, which takes a program
        and the result of the liveness analysis as input and computes
        the interference graph. This works basically the same as in
        the previous exercise.
        
    -   A function `color_graph`, which takes the interference graph
        and returns a coloring for it. This function works the same as
        in the previous exercise.

    -   A function `assign_locations`, which takes the coloring of the interference graph
        and assigns registers and memory locations to the variables. 
        This function also works the same as in the previous exercise.

## Bonus Task: Faster Liveness Analysis with Strongly Connected Components

The fixpoint computation in the liveness analysis is pretty expensive
with O(n⁴) runtime.

A trick to speed this computation up consists in dividing the control flow graph
into [Strongly Connected Components](https://en.wikipedia.org/wiki/Strongly_connected_component)
and then invoking the fixpoint computation multiple times on smaller graphs.

A *strongly connected component (SCC)* of a graph is a subgraph, where each
node can be reached from every other node (not necessarily directly).

By dividing a directed graph into SCCs, which are as large as
possible, it is ensured that all cycles are within the strongly
connected components, i.e. if there is an edge from a node of one SCC
to a node of another SCC, then there won't be any path back, because otherwise both
nodes would be part of the same SCC.

Consequently, if one builds a directed graph, which has the SCCs of
our original graph as nodes, and an edge between two SCCs iff there
exist edges between a node from one SCC to a node of the other SCC,
then this graph is necessarily acyclic.

If we divide our control flow graph in this way, then we can traverse
the SCCs in topological order and apply the fixpoint computation of
the liveness analysis to each SCC individually. This can significantly
improve runtime, as a large fixpoint computation is replaced by
multiple smaller ones.

Happy Coding! <3

