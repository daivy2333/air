<pir>
<meta>
name: python_project
root: /home/daivy/projects/air/test_projects/python_project
profile: generic
lang: PY
</meta>
<units>
u0: main.py type=PY role=lib module=python_project
u1: calculator.py type=PY role=lib module=python_project
u2: utils.py type=PY role=lib module=python_project
</units>
<dependency-pool>
d0: import:[calculator]
d1: import:[utils]
</dependency-pool>
<dependencies>
u0->refs:[d1 d0]
</dependencies>
<symbols>
main:u0 func entry=true
Calculator:u1 class
greet:u2 func
format_result:u2 func
validate_number:u2 func
</symbols>
<profiles>
  active: python-tool
  python-tool:
    confidence: 0.6
    tags:
      - domain:tooling
      - runtime:cpython
      - stack:python-tool
    signals:
      - entry-point
      - small-project
</profiles>
</pir>