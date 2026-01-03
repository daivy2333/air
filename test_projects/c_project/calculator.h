#ifndef CALCULATOR_H
#define CALCULATOR_H

#define MAX_HISTORY 100

typedef struct {
    double a;
    double b;
    double result;
} Calculation;

typedef struct {
    Calculation history[MAX_HISTORY];
    int count;
} Calculator;

void init_calculator(Calculator* calc);
double add(Calculator* calc, double a, double b);
double subtract(Calculator* calc, double a, double b);
double multiply(Calculator* calc, double a, double b);
double divide(Calculator* calc, double a, double b);
void print_history(const Calculator* calc);

#endif
