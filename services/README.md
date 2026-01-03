# AIR Services - 统一接口中心

AIR (Application Interface Center) 提供了统一的命令行接口来调用正向和逆向工具。

## 使用方式

### 正向生成 PIR

从源代码生成 PIR 文件：

```bash
python3 app.py forward /path/to/project
```

可选参数：

- `-o, --out`: 指定输出 PIR 文件路径（默认：`<project_name>.pir`）
- `--profile`: 指定配置文件名称（默认：`generic`）
- `--name`: 指定项目名称（默认：目录名）
- `--no-cache`: 禁用分析缓存

示例：

```bash
# 基本使用
python3 app.py forward /road

# 指定输出文件
python3 app.py forward /road -o my_project.pir

# 使用特定配置
python3 app.py forward /road --profile rust
```

### 逆向重构项目

从 PIR 文件重构项目：

```bash
python3 app.py reverse example.pir output/
```

可选参数：

- `--project-root`: 指定项目根目录（默认：PIR 文件所在目录）
- `--validate-only`: 仅验证 PIR 文件而不进行重构

示例：

```bash
# 基本使用
python3 app.py reverse example.pir output/

# 仅验证 PIR
python3 app.py reverse example.pir output/ --validate-only

# 指定项目根目录
python3 app.py reverse example.pir output/ --project-root /path/to/source
```

### 生成 PCES（代码证据）

从 PCR 文件生成 PCES 静态证据：

```bash
python3 app.py peek request.pcr
```

可选参数：

- `--source-dir`: 指定源码目录（默认：PCR 文件所在目录）
- `-o, --output`: 指定输出文件路径（默认：标准输出）

特点：

- 自动查找同目录下的 `.pir` 文件
- 无需手动指定 PIR 路径
- 支持 PCR 规范 v1

示例：

```bash
# 基本使用（自动查找同目录的 .pir 文件）
python3 app.py peek request.pcr

# 指定源码目录
python3 app.py peek request.pcr --source-dir /path/to/source

# 输出到文件
python3 app.py peek request.pcr -o evidence.pces
```

## 项目结构

```
air/
├── app.py              # 统一入口
├── services/
│   ├── forward.py      # 正向服务（PIR 生成）
│   ├── reverse.py      # 逆向服务（项目重构）
│   ├── peek.py         # 证据服务（PCES 生成）
│   └── README.md       # 本文档
├── pirgen/             # 正向引擎
├── pir-reconstructor/  # 逆向引擎
└── pcegen/             # 证据生成引擎
```

## 架构说明

### 服务层（services/）

- `forward.py`: 封装 pirgen 的功能，提供 PIR 生成服务
- `reverse.py`: 封装 pir-reconstructor 的功能，提供项目重构服务
- `peek.py`: 封装 pcegen 的功能，提供 PCES 生成服务

### 应用层（app.py）

- 提供统一的命令行接口
- 调用相应的服务层功能
- 处理命令行参数和错误

## 优势

1. **统一接口**: 不需要分别进入 pirgen 和 pir-reconstructor 目录
2. **简化使用**: 所有操作通过 `app.py` 一个入口完成
3. **易于扩展**: 可以方便地添加新的功能和服务
