#include <iostream>
#include <memory>

// C++ 主程序，调用其他语言的模块
extern "C" {
    // C 函数声明
    int c_calculate_sum(int a, int b);
    void c_print_message(const char* msg);
}

// Rust 函数声明
extern "C" {
    int rust_calculate_product(int a, int b);
    void rust_print_stats(int count, int total);
}

int main() {
    std::cout << "=== Cross-Language Project ===" << std::endl;

    // 使用 C 函数
    int sum = c_calculate_sum(10, 20);
    c_print_message("Calculation completed");

    // 使用 Rust 函数
    int product = rust_calculate_product(sum, 3);
    rust_print_stats(2, sum + product);

    std::cout << "Final Result: " << (sum + product) << std::endl;

    return 0;
}
