#include <sstream>
#include <iomanip>
#include "utils.h"

std::string greet(const std::string& name) {
    return "Hello, " + name + "!";
}

std::string format_result(const std::string& expression, double result) {
    std::ostringstream oss;
    oss << expression << " = " << std::fixed << std::setprecision(2) << result;
    return oss.str();
}

bool validate_number(const std::string& value) {
    if (value.empty()) {
        return false;
    }

    bool has_decimal = false;
    bool has_digit = false;

    for (char c : value) {
        if (c == '.') {
            if (has_decimal) {
                return false;  // 多个小数点
            }
            has_decimal = true;
        } else if (!std::isdigit(c) && c != '-' && c != '+') {
            return false;  // 非法字符
        } else if (std::isdigit(c)) {
            has_digit = true;
        }
    }

    return has_digit;
}
