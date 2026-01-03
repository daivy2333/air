<pir>
<meta>
name: rust_project
root: /home/daivy/projects/air/test_projects/rust_project
profile: generic
lang: Rust
</meta>
<units>
u0: calculator.rs type=Rust role=lib module=rust_project
u1: main.rs type=Rust role=lib module=rust_project
u2: utils.rs type=Rust role=lib module=rust_project
</units>
<dependency-pool>
d0: use:[calculator::Calculator]
d1: use:[utils::{greet, format_result}]
</dependency-pool>
<dependencies>
u1->refs:[d0 d1]
</dependencies>
<symbols>
new:u0 func
new:u0 func
add:u0 func
subtract:u0 func
multiply:u0 func
divide:u0 func
get_history:u0 func
print_history:u0 func
add_to_history:u0 func
Calculation:u0 struct
Calculator:u0 struct
main:u1 func entry=true
greet:u2 func
format_result:u2 func
validate_number:u2 func
</symbols>
</pir>