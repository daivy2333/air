#[derive(Debug, Clone)]
pub struct Calculation {
    pub a: f64,
    pub b: f64,
    pub result: f64,
}

impl Calculation {
    pub fn new(a: f64, b: f64, result: f64) -> Self {
        Calculation { a, b, result }
    }
}

pub struct Calculator {
    history: Vec<Calculation>,
}

impl Calculator {
    pub fn new() -> Self {
        Calculator {
            history: Vec::with_capacity(100),
        }
    }

    pub fn add(&mut self, a: f64, b: f64) -> f64 {
        let result = a + b;
        self.add_to_history(a, b, result);
        result
    }

    pub fn subtract(&mut self, a: f64, b: f64) -> f64 {
        let result = a - b;
        self.add_to_history(a, b, result);
        result
    }

    pub fn multiply(&mut self, a: f64, b: f64) -> f64 {
        let result = a * b;
        self.add_to_history(a, b, result);
        result
    }

    pub fn divide(&mut self, a: f64, b: f64) -> Result<f64, String> {
        if b == 0.0 {
            return Err("Division by zero".to_string());
        }
        let result = a / b;
        self.add_to_history(a, b, result);
        Ok(result)
    }

    pub fn get_history(&self) -> &[Calculation] {
        &self.history
    }

    pub fn print_history(&self) {
        println!("\nCalculation History:");
        for calc in &self.history {
            println!("{} + {} = {}", calc.a, calc.b, calc.result);
        }
    }

    fn add_to_history(&mut self, a: f64, b: f64, result: f64) {
        self.history.push(Calculation::new(a, b, result));
    }
}
