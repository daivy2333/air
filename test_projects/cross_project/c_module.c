#include <stdio.h>

// C 函数实现，供其他语言调用
int c_calculate_sum(int a, int b) {
    return a + b;
}

void c_print_message(const char* msg) {
    printf("[C Module] %s\n", msg);
}

// 内部辅助函数
static int internal_multiply(int a, int b) {
    return a * b;
}

// 公开的辅助函数
int c_calculate_power(int base, int exp) {
    int result = 1;
    for (int i = 0; i < exp; i++) {
        result = internal_multiply(result, base);
    }
    return result;
}
