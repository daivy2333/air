#include <iostream>
#include "calculator.h"

Calculator::Calculator() {
    history.reserve(100);
}

Calculator::~Calculator() {
    // 析构函数
}

double Calculator::add(double a, double b) {
    double result = a + b;
    addToHistory(a, b, result);
    return result;
}

double Calculator::subtract(double a, double b) {
    double result = a - b;
    addToHistory(a, b, result);
    return result;
}

double Calculator::multiply(double a, double b) {
    double result = a * b;
    addToHistory(a, b, result);
    return result;
}

double Calculator::divide(double a, double b) {
    if (b == 0.0) {
        throw std::runtime_error("Division by zero");
    }
    double result = a / b;
    addToHistory(a, b, result);
    return result;
}

void Calculator::addToHistory(double a, double b, double result) {
    history.emplace_back(a, b, result);
}

void Calculator::printHistory() const {
    std::cout << "\nCalculation History:" << std::endl;
    for (const auto& calc : history) {
        std::cout << calc.a << " + " << calc.b << " = " << calc.result << std::endl;
    }
}

const std::vector<Calculation>& Calculator::getHistory() const {
    return history;
}
