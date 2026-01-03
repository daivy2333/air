#include <stdio.h>
#include "calculator.h"

void init_calculator(Calculator* calc) {
    calc->count = 0;
}

double add(Calculator* calc, double a, double b) {
    double result = a + b;
    if (calc->count < MAX_HISTORY) {
        calc->history[calc->count].a = a;
        calc->history[calc->count].b = b;
        calc->history[calc->count].result = result;
        calc->count++;
    }
    return result;
}

double subtract(Calculator* calc, double a, double b) {
    double result = a - b;
    if (calc->count < MAX_HISTORY) {
        calc->history[calc->count].a = a;
        calc->history[calc->count].b = b;
        calc->history[calc->count].result = result;
        calc->count++;
    }
    return result;
}

double multiply(Calculator* calc, double a, double b) {
    double result = a * b;
    if (calc->count < MAX_HISTORY) {
        calc->history[calc->count].a = a;
        calc->history[calc->count].b = b;
        calc->history[calc->count].result = result;
        calc->count++;
    }
    return result;
}

double divide(Calculator* calc, double a, double b) {
    if (b == 0.0) {
        printf("Error: Division by zero\n");
        return 0.0;
    }
    double result = a / b;
    if (calc->count < MAX_HISTORY) {
        calc->history[calc->count].a = a;
        calc->history[calc->count].b = b;
        calc->history[calc->count].result = result;
        calc->count++;
    }
    return result;
}

void print_history(const Calculator* calc) {
    printf("\nCalculation History:\n");
    for (int i = 0; i < calc->count; i++) {
        printf("%.2f + %.2f = %.2f\n", 
               calc->history[i].a, 
               calc->history[i].b, 
               calc->history[i].result);
    }
}
