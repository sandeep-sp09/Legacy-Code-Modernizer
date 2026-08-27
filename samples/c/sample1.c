#include <stdio.h>

int add_numbers(int a, int b) {
    return a + b;
}

int main() {
    int x = 5, y = 10;
    int sum = add_numbers(x, y);
    printf("Sum is: %d\n", sum);
    return 0;
}
