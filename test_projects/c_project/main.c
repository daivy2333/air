#include <stdio.h>
#include "calculator.h"
#include "utils.h"

int main() {
    printf("%s
", greet("C Calculator"));

    Calculator calc;
    init_calculator(&calc);

    // 执行一些计算
    double result1 = add(&calc, 10, 5);
    printf("%s
", format_result("10 + 5", result1));

    double result2 = multiply(&calc, result1, 2);
    printf("%s
", format_result("(10 + 5) * 2", result2));

    double result3 = divide(&calc, result2, 3);
    printf("%s
", format_result("(10 + 5) * 2 / 3", result3));

    print_history(&calc);

    return 0;
}
