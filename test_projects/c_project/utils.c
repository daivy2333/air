#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "utils.h"

char* greet(const char* name) {
    static char buffer[256];
    snprintf(buffer, sizeof(buffer), "Hello, %s!", name);
    return buffer;
}

char* format_result(const char* expression, double result) {
    static char buffer[256];
    snprintf(buffer, sizeof(buffer), "%s = %.2f", expression, result);
    return buffer;
}

int validate_number(const char* value) {
    if (value == NULL || *value == '\0') {
        return 0;
    }

    int has_decimal = 0;
    int has_digit = 0;

    for (int i = 0; value[i] != '\0'; i++) {
        if (value[i] == '.') {
            if (has_decimal) {
                return 0;  // 多个小数点
            }
            has_decimal = 1;
        } else if (!isdigit(value[i]) && value[i] != '-' && value[i] != '+') {
            return 0;  // 非法字符
        } else if (isdigit(value[i])) {
            has_digit = 1;
        }
    }

    return has_digit;
}
