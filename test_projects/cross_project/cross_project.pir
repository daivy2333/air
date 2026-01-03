<pir>
<meta>
name: cross_project
root: /home/daivy/projects/air/test_projects/cross_project
profile: generic
lang: C,CPP,Rust
</meta>
<units>
u0: c_module.c type=C role=lib module=cross_project
u1: rust_module.rs type=Rust role=lib module=cross_project
u2: main.cpp type=CPP role=lib module=cross_project
</units>
<dependency-pool>
d0: include:[iostream]
d1: include:[memory]
d2: include:[stdlib:c]
d3: use:[core::panic::PanicInfo]
</dependency-pool>
<dependencies>
u0->refs:[d2]
u1->refs:[d3]
u2->refs:[d0 d1]
</dependencies>
<symbols>
c_calculate_sum:u0 func
c_print_message:u0 func
internal_multiply:u0 func
c_calculate_power:u0 func
panic:u1 func
internal_divide:u1 func
main:u2 func entry=true
</symbols>
<profiles>
  active: c-framework
  c-framework:
    confidence: 0.5
    tags:
      - domain:language-tooling
      - runtime:native
      - stack:c-framework
  system-c:
    confidence: 0.4
    tags:
      - domain:system
      - lang:c
      - runtime:native
</profiles>
</pir>