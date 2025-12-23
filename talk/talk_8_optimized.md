# Profile 推断优化方案

## 问题描述

Rust 和 C++ 项目被错误地识别为 python-tool 类型，profile 推断结果不准确。

### 主要问题

1. **语言识别错误**：Rust 项目被识别为 python-tool（置信度 0.6）
2. **特征匹配不准确**：C++ 项目也被识别为 python-tool，同时有一个低置信度的 system-c profile
3. **信号分析偏差**：依赖分析未能正确识别语言特定特征

## 已实现的优化

### 1. 新增 Profile 规则定义

#### Rust 学习项目特征
```python
RUST_LEARNING_PATTERNS = {
    "algorithm", "leetcode", "binary-search",
    "dynamic-programming", "graph", "tree", "sorting",
}

RUST_MODULE_PATTERNS = {
    "mod.rs", "lib.rs", "main.rs",
}
```

#### C++ 竞赛编程特征
```python
CPP_COMPETITIVE_PATTERNS = {
    "icpc", "acm", "codeforces", "atcoder", "leetcode", "hackerrank",
}

CPP_STD_HEADERS = {
    "iostream", "vector", "algorithm", "string",
    "map", "set", "queue", "stack",
}
```

### 2. 新增 Profile 检测方法

#### `rust-learning` Profile

检测规则：
- Rust stdlib 目标存在
- 文件路径包含算法学习模式
- 模块结构（mod.rs, lib.rs, main.rs）
- 无重型框架依赖（web, embedded）

置信度计算：
- 学习模式：+0.3
- 模块结构：+0.25
- stdlib 存在：+0.2
- 多文件：+0.15
- 纯学习（无框架）：+0.1

#### `cpp-competitive` Profile

检测规则：
- C/C++ stdlib 目标存在
- 文件路径包含竞赛编程模式
- 标准库头文件使用
- 竞赛编程特定模式（如 bits/stdc++.h）

置信度计算：
- 竞赛模式：+0.4
- 标准头文件：+0.2
- bits/stdc++.h：+0.15
- LeetCode 模式：+0.25
- 多文件：+0.15

### 3. 语言冲突检测优化

在 `_detect_python_tool` 方法中添加语言冲突检测：

```python
# 语言冲突检查：如果项目有非 Python 语言，
# 只有在 Python 是主导语言时才检测 python-tool
if model.langs and len(model.langs) > 1:
    if "PY" not in model.langs:
        return None
    # 统计各语言文件数
    lang_counts = {}
    for unit in model.units:
        lang_counts[unit.lang] = lang_counts.get(unit.lang, 0) + 1
    # Python 必须是主导语言（> 50%）
    py_count = lang_counts.get("PY", 0)
    total_count = sum(lang_counts.values())
    if py_count / total_count <= 0.5:
        return None
```

## 预期修复结果

### Rust 项目预期输出

```xml
<profiles>
  active: rust-learning
  rust-learning:
    confidence: 0.85
    tags:
      - lang:rust
      - purpose:learning
      - domain:algorithms
      - ecosystem:cargo
      - build:rustc
    signals:
      - learning-patterns
      - mod-structure
      - rust-stdlib
      - multi-unit
      - pure-learning
</profiles>
```

### C++ 项目预期输出

```xml
<profiles>
  active: cpp-competitive
  cpp-competitive:
    confidence: 0.80
    tags:
      - lang:cpp
      - domain:competitive-programming
      - purpose:icpc
      - pattern:leetcode
      - difficulty:mixed
      - module-organized
    signals:
      - competitive-patterns
      - std-headers
      - bits-stdcpp
      - leetcode-patterns
      - multi-unit
</profiles>
```

## 实现文件

所有优化已实现在 `pirgen/core/profile_canon.py` 文件中，包括：
- 新增 `RUST_LEARNING_PATTERNS` 和 `RUST_MODULE_PATTERNS` 常量
- 新增 `CPP_COMPETITIVE_PATTERNS` 和 `CPP_STD_HEADERS` 常量
- 新增 `_detect_rust_learning` 方法
- 新增 `_detect_cpp_competitive` 方法
- 改进 `_detect_python_tool` 方法，添加语言冲突检测
