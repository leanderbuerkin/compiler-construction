from typing import Literal

def riscv_01() -> int:
    """
    Question:
        How many bytes does a stack frame require that needs to save three local variables?
    
    Returns:
        The number of bytes that the stack pointer has to be lowered to accomodate the stack frame.

    3 Variables need 8*3=24 bytes
    return address and frame pointer need 2*8=16 bytes
    40 bytes aligned for 16 bytes equals 48 bytest
    """
    return 48

def lexer_01() -> bool:
    """
    Question:
        A lexer is usually described by a mapping from context free grammars to tokens.
        True or false?
        
    Returns:
        Whether the statement is true or false.
    """
    return False

def parser_01() -> Literal["O(n)", "O(n**2)", "O(n**3)"]:
    """
    Question:
        What is the worst case time complexity for unambigous grammars for the Early Parser algorithm?
        
    Returns:
        The correct complexity class.
    """
    return "O(n**2)"

def register_allocation_01() -> bool:
    """
    Question:
        The live-before set of the first instruction of a basic block is always empty when the control flow graph is acyclic.
        True or false?
    
    Returns:
        Whether the statement is true or false.
    """
    return False

def register_allocation_02() -> set[Literal["a", "b", "c"]]:
    """
    Question:
        What is the live-after set of instruction 2 in the following example?
            1: mv a 5
            2: mv b 30
            3: add c a b
            4: mv b 10
            5: add b b c
    
    Returns:
        The correct set of variables.
    """
    return {"a", "b"}

def register_allocation_03() -> Literal["P", "NP", "Co-NP", "PSPACE", "EXPTIME"]:
    """
    Question:
        Optimal register allocation for variables is complete for which complexity class?
    
    Returns:
        The name of the complexity class.
    """
    return "NP"

def garbage_collection_01() -> Literal["depth-first search", "breadth-first search", "binary search"]:
    """
    Question:
        The copying collection garbage collector performs which kind of search?
    
    Returns:
        The correct answer.
    """
    return "breadth-first search"

def garbage_collection_02() -> int:
    """
    Question:
        Given a copying collector with a from- and to-space of 1024 bytes respectively.
        How many bytes are allocated on the heap in the following example?
            1: a = ((1, False)[0], 2)
            2: b = (a, a[1] + 1)
            3: print(b[1])
    
    Returns:
        The number of bytes that were allocated for tuples on the heap during the life time of the example.
    """
    return 9 * 8

def peephole_optimization_01() -> bool:
    """
    Question:
        Classical peephole optimization is performed locally.
        True or false?
    
    Returns:
        Whether the statement is true or false.
    """
    return True

def peephole_optimization_02() -> int:
    """
    Question:
        How many instructions can be removed by applying peephole optimizations (from the lecture) on the following example?
            1: mv x 42
            2: add y x 0
            3: mv x y
            4: mul x x 1
            5: sub x y 0
            6: mul x y 0
    
    Returns:
        How many instructions the optimized example has less than the unoptimized example.
    """
    return 3