#include <inttypes.h> // for int64_t typedefs
#include <stdbool.h>  // C-booleans are a typedef to int
#include <stdio.h>    // for debug printing
#include <stdlib.h>   // For malloc
#include <string.h>   // For memcpy

// –– I/O Operations –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

void print_int64(int64_t x) {
    printf("%" PRId64 "\n", x);
}

int64_t input_int64() {
    int64_t x;
    int c;

    do {
        if (scanf("%" SCNd64, &x) == 1) 
            break; 

        while ((c = getchar()) != '\n' && c != EOF);
    } while (1);

    return x;
}

