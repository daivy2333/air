#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/daivy/projects/air/pcegen')
from core.pir_index import PIRIndex
from core.pcr_parser import PCRParser
from core.resolver import Resolver
from core.extractor import Extractor
from core.evidence_builder import EvidenceBuilder
from core.serializer import PCESerializer

# 加载 PIR
pir_index = PIRIndex.from_file('pirgen.pir')
pir_data = pir_index.get_pir_data()

# 加载 PCR
with open('test_full.pcr', 'r') as f:
    pcr_text = f.read()

# 解析 PCR
parser = PCRParser()
needs = parser.parse(pcr_text)
print(f'Parsed {len(needs)} needs')

# 初始化组件
resolver = Resolver(pir_data)
extractor = Extractor(pir_data, {})
builder = EvidenceBuilder(extractor)

# 处理所有的needs
for i, need in enumerate(needs):
    print(f'\nProcessing need {i+1}/{len(needs)}: type={need.type}, ref={need.ref}, view={need.view}')
    try:
        resolved_ref = resolver.resolve(need)
        print(f'ResolvedRef: kind={resolved_ref.kind}, unit_id={resolved_ref.unit_id}, symbol={resolved_ref.symbol}')
        evidence = builder.build(need, resolved_ref)
        print(f'Evidence: ref={evidence.ref}, view={evidence.view}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        break
