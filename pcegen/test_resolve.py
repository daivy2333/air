#!/usr/bin/env python3
from core.pir_index import PIRIndex
from core.pcr_parser import PCRParser
from core.resolver import Resolver

# 加载 PIR
pir = PIRIndex.from_file('pcegen.pir')
pir_data = pir.get_pir_data()

# 解析 PCR
parser = PCRParser()
with open('test.pcr', 'r') as f:
    pcr_text = f.read()

needs = parser.parse(pcr_text)

# 测试解析
resolver = Resolver(pir_data)

for need in needs:
    print(f"\n=== {need.type}: {need.ref} ({need.view}) ===")
    resolved = resolver.resolve(need)
    print(f"Resolved: {resolved}")
    print(f"  is_missing: {resolved.is_missing}")
    print(f"  is_ambiguous: {resolved.is_ambiguous}")
    print(f"  kind: {resolved.kind}")
    print(f"  unit_id: {resolved.unit_id}")
    print(f"  symbol: {resolved.symbol}")
