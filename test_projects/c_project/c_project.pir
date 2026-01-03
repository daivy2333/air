<pir>
<meta>
name: c_project
root: /home/daivy/projects/air/test_projects/c_project
profile: generic
lang: C,H
</meta>
<units>
u0: main.c type=C role=lib module=c_project
u1: calculator.c type=C role=lib module=c_project
u2: utils.c type=C role=lib module=c_project
u3: calculator.h type=H role=lib module=c_project
u4: utils.h type=H role=lib module=c_project
</units>
<dependency-pool>
d0: include:[calculator.h]
d1: include:[stdlib:c]
d2: include:[utils.h]
</dependency-pool>
<dependencies>
u0->refs:[d0 d2 d1]
u1->refs:[d0 d1]
u2->refs:[d2 d1]
</dependencies>
<symbols>
main:u0 func entry=true
init_calculator:u1 func
add:u1 func
subtract:u1 func
multiply:u1 func
divide:u1 func
print_history:u1 func
validate_number:u2 func
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