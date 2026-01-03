#include <iostream>
#include <memory>
#include "calculator.h"
#include "utils.h"

int main() {
    std::cout << greet("C++ Calculator") << std::endl;

    auto calc = std::make_unique<Calculator>();

    // 执行一些计算
    double result1 = calc->add(10, 5);
    std::cout << format_result("10 + 5", result1) << std::endl;

    double result2 = calc->multiply(result1, 2);
    std::cout << format_result("(10 + 5) * 2", result2) << std::endl;

    double result3 = calc->divide(result2, 3);
    std::cout << format_result("(10 + 5) * 2 / 3", result3) << std::endl;

    calc->printHistory();

    return 0;
}
