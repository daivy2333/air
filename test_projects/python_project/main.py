#!/usr/bin/env python3
"""Python 测试项目 - 主程序"""

from calculator import Calculator
from utils import greet, format_result


def main():
    """主函数 - 程序入口点"""
    print(greet("Python Calculator"))

    calc = Calculator()

    # 执行一些计算
    result1 = calc.add(10, 5)
    print(format_result("10 + 5", result1))

    result2 = calc.multiply(result1, 2)
    print(format_result("(10 + 5) * 2", result2))

    result3 = calc.divide(result2, 3)
    print(format_result("(10 + 5) * 2 / 3", result3))


if __name__ == "__main__":
    main()
