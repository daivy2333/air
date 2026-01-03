# pcegen - PIR Code Evidence Generator

从 PIR + PCR + 源码生成 PCES 静态证据的工具。

## 功能

pcegen 是一个静态证据生成器，它：
- 解析 PIR（PIR Index Representation）
- 解析 PCR（PIR Code Request）
- 从源码中提取信息
- 生成 PCES（PIR Code Evidence Specification）格式的证据

## 安装

```bash
cd pcegen
```

## 使用方法

```bash
python pcegen.py --pir <pir_file> --pcr <pcr_file> --source-dir <source_directory> [-o <output_file>]
```

### 参数说明

- `--pir`: PIR 文件路径（必需）
- `--pcr`: PCR 文件路径（必需）
- `--source-dir`: 源码目录路径（必需）
- `-o, --output`: 输出文件路径（可选，默认输出到 `<pcr_file>.pcir`）

### 示例

```bash
# 从 PIR、PCR 和源码生成 PCES，自动输出到 <pcr_file>.pcir
python pcegen.py --pir example.pir --pcr request.pcr --source-dir ./src

# 生成 PCES 并保存到指定文件
python pcegen.py --pir example.pir --pcr request.pcr --source-dir ./src -o evidence.pcir
```

### 重要说明

pcegen 的设计目标是保留完整的代码信息，而不是压缩 token：
- 对于 `definition` view：输出完整的函数/类定义代码
- 对于 `api` view：输出完整的签名和定义代码
- 对于 `impl` view：输出完整的实现代码和行为描述

这样可以确保 AI 能够获取到完整的代码上下文，而不是摘要信息。

## 项目结构

```
pcegen/
├── pcegen.py                # CLI 入口
├── core/
│   ├── pir_index.py         # PIR 索引
│   ├── pcr_parser.py        # PCR 解析
│   ├── resolver.py          # ref → 源定位
│   ├── extractor.py         # 最大信息提取
│   ├── compressor.py        # view → 最小证据
│   └── serializer.py        # PCES 输出
├── analyzers/
│   ├── base.py              # 分析器基类
│   ├── python.py            # Python 分析器
│   ├── c.py                 # C 语言分析器
│   ├── rust.py              # Rust 分析器
│   ├── asm.py               # 汇编分析器
│   └── ld.py                # 链接器脚本分析器
└── models/
    ├── need.py              # Need 数据模型
    ├── evidence.py          # Evidence 数据模型
    └── resolved_ref.py      # ResolvedRef 数据模型
```

## 支持的 View 类型

- `exist`: 检查符号是否存在
- `definition`: 获取定义位置和类型
- `api`: 获取导出接口签名
- `impl`: 获取实现摘要
- `asm`: 获取汇编级摘要
- `summary`: 获取结构化语义总结
- `callchain`: 获取调用路径

## 规范

- [PCR 规范](../spec/pcr.md)
- [PCES 规范](../spec/pces.md)

## 许可证

本项目遵循相关开源许可证。
