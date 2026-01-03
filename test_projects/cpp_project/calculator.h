#ifndef CALCULATOR_H
#define CALCULATOR_H

#include <vector>
#include <string>

class Calculation {
public:
    double a;
    double b;
    double result;

    Calculation(double a, double b, double result) 
        : a(a), b(b), result(result) {}
};

class Calculator {
public:
    Calculator();
    virtual ~Calculator();

    double add(double a, double b);
    double subtract(double a, double b);
    double multiply(double a, double b);
    double divide(double a, double b);

    void printHistory() const;
    const std::vector<Calculation>& getHistory() const;

protected:
    std::vector<Calculation> history;

private:
    void addToHistory(double a, double b, double result);
};

#endif
