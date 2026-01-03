mod calculator;
mod utils;

use calculator::Calculator;
use utils::{greet, format_result};

fn main() {
    println!("{}", greet("Rust Calculator"));

    let mut calc = Calculator::new();

    // 执行一些计算
    let result1 = calc.add(10.0, 5.0);
    println!("{}", format_result("10 + 5", result1));

    let result2 = calc.multiply(result1, 2.0);
    println!("{}", format_result("(10 + 5) * 2", result2));

    let result3 = calc.divide(result2, 3.0);
    println!("{}", format_result("(10 + 5) * 2 / 3", result3));

    calc.print_history();
}
