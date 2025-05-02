# Exercise 2

In this exercise, your task is to implement `register allocation` for
the `Lvar` language from chapter 2. This exercise
is based on the exercises from chapter 4 with slight modifications and
a simpler starter codebase.

We made the following changes to the source code:
    
- `src/`:   
    - `register_allocation.py`: added function `allocate_registers` that serves as the entry point for register allocation, alongside a rough structure for the implementation (namely the functions `liveness_and_interference_graph`, `color_graph` and `assign_locations` as well as the `RegAllocOutput` dataclass).
    - `compiler.py`: added call to `allocate_registers` and the delivery of the returned `RegAllocOutput` to the relevant passes (namely `assign homes` and `add prelude and conclusion`)
    - `util/`:
        - `priority_queue.py`: added simple priority queue implementation (for use in the register allocation algorithm)
        - `undirected_graph.py`: added simple undirected graph implementation (for use in the register allocation algorithm)
    - `register.py`: added `CALLEE_SAVED_REGISTERS`, `CALLER_SAVED_REGISTERS` and `FUNCTION_ARG_REGISTERS`.
    - `pass_3_4_assign`: added support for assignment based on registers and stack locations determined by register allocation
    - `pass_5_6_prelude`: added support for the usage of the stack pointer offset calculated by register allocation.

## Tasks

Your tasks is to implement `register_allocation`.

1.  Make yourself familiar with the changes to the code base by reading
    through the source files and matching the code to the concepts
    you've learned in the lectures. 

2.  In `src/register_allocation.py` you should implement register allocation. 
    You can follow the definitions suggested for auxiliary functions from the exercises in chapter 4 of the book.

4.  **Challenge task for motivated students:**  Implement move biasing. Follow chapter 4.7 of the book.
    You may need to modify the `src/util/priority_queue.py` to fit your needs. 

Happy Coding! <3
