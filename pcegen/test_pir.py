#!/usr/bin/env python3
from core.pir_index import PIRIndex
from core.pcr_parser import PCRParser
from core.resolver import Resolver
from core.extractor import Extractor

# 加载 PIR
pir = PIRIndex.from_file('pcegen.pir')
pir_data = pir.get_pir_data()

print("PIR Units:")
for unit in pir_data.get('units', []):
    print(f"  {unit.get('id')}: {unit.get('path')}")

print("\nPIR Symbols:")
for symbol in pir_data.get('symbols', []):
    print(f"  {symbol.get('name')}: {symbol.get('unit')}")

# 测试解析
parser = PCRParser()
with open('test.pcr', 'r') as f:
    pcr_text = f.read()

needs = parser.parse(pcr_text)
print("\nPCR Needs:")
for need in needs:
    print(f"  {need.type}: {need.ref} - {need.view}")

# 测试解析
resolver = Resolver(pir_data)
source_map = {}
for unit in pir_data.get('units', []):
    unit_id = unit.get('id')
    path = unit.get('path')
    if path:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                source_map[unit_id] = f.read()
        except Exception as e:
            print(f"Error loading {path}: {e}")

extractor = Extractor(pir_data, source_map)

print("\nResolved References:")
for need in needs:
    resolved = resolver.resolve(need)
    print(f"  {need.ref} -> {resolved}")
    if not resolved.is_missing:
        info = extractor.extract(resolved)
        print(f"    Info: {info}")
