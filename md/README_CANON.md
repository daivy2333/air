# 依赖语义归一化（Dependency Canonicalization）

## 概述

依赖语义归一化是 PIR 生成过程中的一个重要阶段，它将各种形式的依赖目标（如 `[os]`, `[sys]`, `[stdio.h]` 等）归一化为语义级别的标准形式（如 `[stdlib:py]`, `[stdlib:c]` 等）。

## 设计理念

根据 `talk_3.md` 的指导原则：

- **不需要修改 PIR 核心规范**：依赖归一化属于实现层策略，而非 IR 结构层变更
- **新增独立阶段**：在 `resolve_dependencies` 之后、`finalize_dependencies` 之前添加 `canonicalize_dependencies` 阶段
- **语义增强**：通过归一化，减少 token 数量，同时增强语义表达能力

## Pipeline

完整的 PIR 生成流程：

```
scan_project
  ↓
resolve_dependencies
  ↓
canonicalize_dependencies  ← 新增阶段
  ↓
finalize_dependencies
  ↓
emit PIR
```

## 支持的标准库

### Python 标准库

包括但不限于：
- 基础库：`os`, `sys`, `io`, `json`, `re`, `math`, `string`, `time`
- 数据结构：`collections`, `itertools`, `functools`, `heapq`, `bisect`
- 类型系统：`typing`, `dataclasses`, `enum`, `abc`
- 并发：`threading`, `multiprocessing`, `asyncio`, `queue`
- 网络与通信：`http`, `urllib`, `socket`, `email`
- 文件系统：`pathlib`, `shutil`, `tempfile`
- 日期时间：`datetime`, `calendar`
- 加密与安全：`hashlib`, `secrets`, `ssl`
- 其他：`logging`, `argparse`, `configparser`, `unittest`

### C 标准库

包括但不限于：
- 输入输出：`stdio.h`, `stdlib.h`, `string.h`
- 类型支持：`stdint.h`, `stddef.h`, `stdbool.h`, `inttypes.h`
- 数学函数：`math.h`, `complex.h`, `tgmath.h`, `fenv.h`
- 时间与日期：`time.h`
- 工具函数：`assert.h`, `ctype.h`, `errno.h`, `limits.h`, `float.h`
- 本地化：`locale.h`, `wchar.h`, `wctype.h`
- 信号与进程：`signal.h`, `unistd.h`, `fcntl.h`, `setjmp.h`
- 线程支持：`threads.h`

### Rust 标准库

- 所有以 `std::` 开头的路径都归一化为 `[stdlib:rust]`

## 效果示例

### 归一化前

```text
<dependency-pool>
d0: import:[os]
d1: import:[sys]
d2: import:[argparse]
d3: import:[ast]
d4: import:[typing]
d5: import:[dataclasses]
d6: import:[abc]
d7: import:[re]
</dependency-pool>
```

### 归一化后

```text
<dependency-pool>
d0: import:[stdlib:py]
</dependency-pool>
```

## API

### `canonicalize_target(verb: str, target: str) -> str`

将单个依赖目标归一化为语义形式。

**参数：**
- `verb`: 依赖动词（import/include/use/link等）
- `target`: 原始目标（如 `[os]`, `[stdio.h]` 等）

**返回：**
- 归一化后的目标字符串

### `canonicalize_dependencies(model)`

对整个 ProjectModel 应用依赖归一化。

**参数：**
- `model`: ProjectModel 实例

**注意：**
- 必须在 `finalize_dependencies` 之前调用
- 会修改 model 的 `_unit_dep_keys` 和 `_all_dep_keys`

## 扩展指南

如需添加新的标准库或自定义归一化规则：

1. 在 `PY_STDLIB`、`C_STDLIB` 或其他集合中添加相应的库名
2. 在 `canonicalize_target` 函数中添加新的归一化逻辑
3. 如需支持新的语言，创建新的标准库集合和前缀定义

## 注意事项

1. 归一化不会影响项目内部依赖的解析
2. 只有标准库依赖会被归一化，外部依赖保持原样
3. 归一化过程在依赖解析之后进行，确保符号引用的正确性
