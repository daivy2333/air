"""
Peek service for PCES generation
Wraps pcegen functionality
"""
import os
import sys
from pathlib import Path

# Add pcegen to path
pcegen_path = Path(__file__).parent.parent.parent / "pcegen"
sys.path.insert(0, str(pcegen_path))

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


def run_peek(
    pcr_path: str,
    source_dir: str | None = None,
    output: str | None = None
):
    """
    Run peek operation to generate PCES from PCR

    Args:
        pcr_path: Path to PCR file
        source_dir: Directory containing source code (optional, defaults to current directory)
        output: Output file path (optional, defaults to stdout)

    Returns:
        Path to generated PCES file or None if output to stdout
    """
    # 加载 PCR
    pcr_file = Path(pcr_path)
    if not pcr_file.exists():
        raise ValueError(f"PCR file not found: {pcr_file}")

    with open(pcr_file, 'r', encoding='utf-8') as f:
        pcr_text = f.read()

    # 确定源码目录
    if source_dir is None:
        source_dir = str(pcr_file.parent)
    source_dir_path = Path(source_dir)
    if not source_dir_path.exists():
        raise ValueError(f"Source directory not found: {source_dir_path}")

    # 自动查找 PIR 文件
    pir_file = None
    # 优先查找与 PCR 同名的 PIR 文件（替换.pcr后缀为.pir）
    stem = pcr_file.stem
    potential_pir = source_dir_path / f"{stem}.pir"
    if potential_pir.exists():
        pir_file = potential_pir
    else:
        # 在当前目录查找 PIR 文件
        for f in source_dir_path.glob('*.pir'):
            pir_file = f
            break

    if pir_file is None:
        raise ValueError(f"No PIR file found in {source_dir_path}")

    # 加载 PIR
    pir_index = PIRIndex.from_file(str(pir_file))
    pir_data = pir_index.get_pir_data()

    # 加载源码
    source_code_map = load_source_code(pir_data, source_dir_path)

    # 处理 PCR，生成 PCES
    pces_text = process_pcr(pir_index, pcr_text, source_code_map)

    # 输出结果
    if output:
        output_path = Path(output)
    else:
        # 自动生成与PCR同名的.pcir文件
        output_path = pcr_file.with_suffix('.pcir')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pces_text)
    return str(output_path)
