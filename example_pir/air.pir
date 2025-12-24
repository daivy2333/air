<pir>
<meta>
name: air
root: /home/daivy/projects/air/air
profile: generic
lang: PY
</meta>
<units>
u0: app.py type=PY role=lib module=air
u1: __main__.py type=PY role=lib module=air
u2: __init__.py type=PY role=lib module=air
u3: services/__init__.py type=PY role=lib module=services
u4: services/forward.py type=PY role=lib module=services
u5: services/reverse.py type=PY role=lib module=services
</units>
<dependency-pool>
d0: import:[.app]
d1: import:[air.services.forward]
d2: import:[air.services.reverse]
d3: import:[pir_reconstructor.errors]
d4: import:[pir_reconstructor.pir.parser]
d5: import:[pir_reconstructor.pir.validator]
d6: import:[pir_reconstructor.reconstruct.pipeline]
d7: import:[pirgen.analyzers]
d8: import:[pirgen.core.dep_canon]
d9: import:[pirgen.core.pir_builder]
d10: import:[pirgen.core.profile_canon]
d11: import:[pirgen.core.project_model]
d12: import:[pirgen]
d13: import:[stdlib:py]
</dependency-pool>
<dependencies>
u0->refs:[d13 d1 d2]
u1->refs:[d0]
u4->refs:[d13 d11 d9 d8 d10 d7 d12]
u5->refs:[d13 d4 d5 d6 d3]
</dependencies>
<symbols>
main:u0 func entry=true
run_forward:u4 func
run_reverse:u5 func
</symbols>
</pir>