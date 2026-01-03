#!/usr/bin/env python3
"""
pcegen - PIR Code Evidence Generator
从 PIR + PCR + 源码生成 PCES 静态证据
"""

import argparse
import json
import sys
from pathlib import Path

from core.pir_index import PIRIndex
from core.pcr_parser import PCRParser
from core.resolver import Resolver
from core.extractor import Extractor
from core.evidence_builder import EvidenceBuilder
from core.serializer import PCESerializer


def load_source_code(pir_data: dict, source_dir: Path) -> dict:
    """
    加载源码文件

    Args:
        pir_data: PIR 数据
        source_dir: 源码目录

    Returns:
        {unit_id: source_code} 映射
    """
    source_map = {}

    for unit in pir_data.get('units', []):
        unit_id = unit.get('id')
        path = unit.get('path')

        if path:
            source_path = source_dir / path
            if source_path.exists():
                with open(source_path, 'r', encoding='utf-8') as f:
                    source_map[unit_id] = f.read()

    return source_map


def process_pcr(pir_index: PIRIndex, pcr_text: str, source_code_map: dict) -> str:
    """
    处理 PCR 请求，生成 PCES

    Args:
        pir_index: PIR 索引
        pcr_text: PCR 文本
        source_code_map: 源码映射

    Returns:
        PCES 文本
    """
    # 解析 PCR
    parser = PCRParser()
    needs = parser.parse(pcr_text)

    if not needs:
        raise ValueError("No valid needs found in PCR")

    # 获取 PIR 数据
    pir_data = pir_index.get_pir_data()

    # 初始化各个组件
    resolver = Resolver(pir_data)
    extractor = Extractor(pir_data, source_code_map)
    builder = EvidenceBuilder(extractor)

    # 处理每个 need
    evidences = []
    for need in needs:
        # 解析引用
        resolved_ref = resolver.resolve(need)

        # 构建证据
        evidence = builder.build(need, resolved_ref)
        evidences.append(evidence)

    # 序列化为 PCES
    serializer = PCESerializer()
    pces_text = serializer.serialize(evidences)

    return pces_text


def main():
    parser = argparse.ArgumentParser(
        description='Generate PCES from PIR + PCR + source code'
    )
    parser.add_argument(
        '--pir',
        required=True,
        help='Path to PIR file'
    )
    parser.add_argument(
        '--pcr',
        required=True,
        help='Path to PCR file'
    )
    parser.add_argument(
        '--source-dir',
        required=True,
        help='Directory containing source code'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output file path (default: <pcr_file>.pcir)'
    )

    args = parser.parse_args()

    # 加载 PIR
    pir_path = Path(args.pir)
    if not pir_path.exists():
        print(f"Error: PIR file not found: {pir_path}", file=sys.stderr)
        sys.exit(1)

    pir_index = PIRIndex.from_file(str(pir_path))

    # 加载 PCR
    pcr_path = Path(args.pcr)
    if not pcr_path.exists():
        print(f"Error: PCR file not found: {pcr_path}", file=sys.stderr)
        sys.exit(1)

    with open(pcr_path, 'r', encoding='utf-8') as f:
        pcr_text = f.read()

    # 加载源码
    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}", file=sys.stderr)
        sys.exit(1)

    pir_data = pir_index.get_pir_data()
    source_code_map = load_source_code(pir_data, source_dir)

    # 处理 PCR，生成 PCES
    try:
        pces_text = process_pcr(pir_index, pcr_text, source_code_map)
    except Exception as e:
        print(f"Error processing PCR: {e}", file=sys.stderr)
        sys.exit(1)

    # 输出结果
    if args.output:
        output_path = Path(args.output)
    else:
        # 默认输出到 <pcr_file>.pcir
        output_path = pcr_path.with_suffix('.pcir')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pces_text)

    print(f"PCES generated: {output_path}")


if __name__ == '__main__':
    main()
