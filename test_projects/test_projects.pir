<pir>
<meta>
name: test_projects
root: /home/daivy/projects/air/test_projects
profile: generic
lang: C,CPP,H,PY,Rust,S
</meta>
<units>
u0: cpp_project/calculator.h type=H role=lib module=cpp_project
u1: cpp_project/calculator.cpp type=CPP role=lib module=cpp_project
u2: cpp_project/utils.cpp type=CPP role=lib module=cpp_project
u3: cpp_project/main.cpp type=CPP role=lib module=cpp_project
u4: cpp_project/utils.h type=H role=lib module=cpp_project
u5: cross_project/check_char.py type=PY role=lib module=cross_project
u6: cross_project/c_module.c type=C role=lib module=cross_project
u7: cross_project/rust_module.rs type=Rust role=lib module=cross_project
u8: cross_project/check_all_parentheses.py type=PY role=lib module=cross_project
u9: cross_project/check_cpp_parentheses.py type=PY role=lib module=cross_project
u10: cross_project/main.cpp type=CPP role=lib module=cross_project
u11: cross_project/check_rust_parentheses.py type=PY role=lib module=cross_project
u12: cross_project/check_pos27.py type=PY role=lib module=cross_project
u13: cross_project/check_parentheses.py type=PY role=lib module=cross_project
u14: python_project/main.py type=PY role=lib module=python_project
u15: python_project/calculator.py type=PY role=lib module=python_project
u16: python_project/utils.py type=PY role=lib module=python_project
u17: rust_project/calculator.rs type=Rust role=lib module=rust_project
u18: rust_project/main.rs type=Rust role=lib module=rust_project
u19: rust_project/utils.rs type=Rust role=lib module=rust_project
u20: c_project/main.c type=C role=lib module=c_project
u21: c_project/calculator.c type=C role=lib module=c_project
u22: c_project/utils.c type=C role=lib module=c_project
u23: c_project/calculator.h type=H role=lib module=c_project
u24: c_project/utils.h type=H role=lib module=c_project
u25: os_project/scheduler.h type=H role=lib module=os_project
u26: os_project/scheduler.c type=C role=lib module=os_project
u27: os_project/mm.c type=C role=lib module=os_project
u28: os_project/boot.S type=S role=lib module=os_project
u29: os_project/mm.h type=H role=lib module=os_project
u30: asm_project/start.S type=S role=lib module=asm_project
</units>
<dependency-pool>
d0: call:[.]
d1: call:[check_interrupts]
d2: call:[intc_init]
d3: call:[main]
d4: call:[timer_init]
d5: call:u26#schedule
d6: call:u26#scheduler_init
d7: call:u27#mm_init
d8: call:u28#enable_interrupts
d9: call:u28#kernel_entry
d10: call:u28#kernel_init
d11: call:u28#kernel_main
d12: call:u30#check_events
d13: call:u30#delay
d14: call:u30#init_gpio
d15: call:u30#init_system
d16: call:u30#init_timer
d17: call:u30#init_uart
d18: call:u30#main_loop
d19: call:u30#process_events
d20: import:[calculator]
d21: import:[stdlib:py]
d22: import:[utils]
d23: include:[calculator.h]
d24: include:[iomanip]
d25: include:[iostream]
d26: include:[memory]
d27: include:[sstream]
d28: include:[stdlib:c]
d29: include:[stdlib:py]
d30: include:[utils.h]
d31: include:[vector]
d32: use:[calculator::Calculator]
d33: use:[core::panic::PanicInfo]
d34: use:[utils::{greet, format_result}]
</dependency-pool>
<dependencies>
u0->refs:[d29 d31]
u1->refs:[d25 d23]
u2->refs:[d30 d27 d24]
u3->refs:[d30 d25 d26 d23]
u4->refs:[d29]
u5->refs:[d21]
u6->refs:[d28]
u7->refs:[d33]
u8->refs:[d21]
u9->refs:[d21]
u10->refs:[d25 d26]
u11->refs:[d21]
u13->refs:[d21]
u14->refs:[d22 d20]
u18->refs:[d34 d32]
u20->refs:[d30 d28 d23]
u21->refs:[d28 d23]
u22->refs:[d30 d28]
u25->refs:[d28]
u26->refs:[d28]
u27->refs:[d28]
u28->refs:[d1 d0 d6 d7 d5 d4 d10 d9 d11 d8 d2]
u29->refs:[d28]
u30->refs:[d14 d13 d12 d18 d3 d16 d17 d19 d15]
</dependencies>
<symbols>
validate_number:u2 func
main:u3 func entry=true
c_calculate_sum:u6 func
c_print_message:u6 func
internal_multiply:u6 func
c_calculate_power:u6 func
panic:u7 func
internal_divide:u7 func
main:u10 func entry=true
main:u14 func entry=true
Calculator:u15 class
greet:u16 func
format_result:u16 func
validate_number:u16 func
new:u17 func
new:u17 func
add:u17 func
subtract:u17 func
multiply:u17 func
divide:u17 func
get_history:u17 func
print_history:u17 func
add_to_history:u17 func
Calculation:u17 struct
Calculator:u17 struct
main:u18 func entry=true
greet:u19 func
format_result:u19 func
validate_number:u19 func
main:u20 func entry=true
init_calculator:u21 func
add:u21 func
subtract:u21 func
multiply:u21 func
divide:u21 func
print_history:u21 func
validate_number:u22 func
scheduler_init:u26 func
schedule:u26 func
terminate_task:u26 func
block_task:u26 func
wakeup_task:u26 func
mm_init:u27 func
kfree:u27 func
init_page_tables:u27 func
_start:u28 label
kernel_entry:u28 label
kernel_init:u28 label
enable_interrupts:u28 label
kernel_main:u28 label
_stack_bottom:u28 label
_stack_top:u28 label
_start:u30 label
main:u30 label
init_system:u30 label
main_loop:u30 label
init_gpio:u30 label
init_uart:u30 label
init_timer:u30 label
check_events:u30 label
process_events:u30 label
delay:u30 label
</symbols>
<profiles>
  active: system-c
  c-framework:
    confidence: 0.5
    tags:
      - domain:language-tooling
      - runtime:native
      - stack:c-framework
  system-c:
    confidence: 0.55
    tags:
      - domain:system
      - lang:c
      - runtime:native
    signals:
      - multi-unit
</profiles>
</pir>