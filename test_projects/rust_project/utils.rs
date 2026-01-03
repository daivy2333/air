pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

pub fn format_result(expression: &str, result: f64) -> String {
    format!("{} = {:.2}", expression, result)
}

pub fn validate_number(value: &str) -> bool {
    if value.is_empty() {
        return false;
    }

    let mut has_decimal = false;
    let mut has_digit = false;

    for c in value.chars() {
        if c == '.' {
            if has_decimal {
                return false;  // 多个小数点
            }
            has_decimal = true;
        } else if !c.is_ascii_digit() && c != '-' && c != '+' {
            return false;  // 非法字符
        } else if c.is_ascii_digit() {
            has_digit = true;
        }
    }

    has_digit
}
