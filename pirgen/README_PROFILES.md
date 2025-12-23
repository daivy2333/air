# PIR v0.4 - Multi-Language Profile Support

## 概述

PIR v0.4 现在支持多语言的 profile 检测，包括 Python、C、Rust 和 Java。每个 profile 都基于项目的依赖模式、文件结构和语义信号进行推断。

## 支持的 Profile

### Python Profiles

#### ml-python
- **检测规则**: 出现 numpy、torch、tensorflow 等 ML 库
- **置信度**: 基于检测到的 ML 库数量 (0.5 + n * 0.1, max 1.0)
- **标签**: domain:ml, runtime:cpython, stack:ml-python, lib:xxx

#### python-tool
- **检测规则**: 出现 stdlib、argparse、pathlib 等工具库
- **置信度**: 基于检测到的工具库数量 (0.3 + n * 0.05, max 0.8)
- **标签**: domain:tooling, runtime:cpython, stack:python-tool, lib:xxx

### C Profiles

#### system-c
- **检测规则**: 
  - 项目包含 C 语言文件
  - 出现 stdlib:c 或 libc
  - 多单元项目 (>10 units) 获得加分
  - 内核相关目录名 (arch, mm, sched, irq) 获得加分
- **置信度**: 基础 0.4 + 多单元加分 (0.15) + 内核信号加分 (0.25), max 0.9
- **标签**: domain:system, lang:c, runtime:native
- **信号**: multi-unit, kernel-layout

#### embedded-c
- **检测规则**: 出现 newlib、musl、freertos、zephyr 等嵌入式 C 库
- **置信度**: 基础 0.6 + n * 0.1, max 0.9
- **标签**: domain:embedded, lang:c, runtime:baremetal, lib:xxx

### Rust Profiles

#### rust-embedded
- **检测规则**: 
  - 项目包含 Rust 语言文件
  - 出现 riscv-rt、embedded-hal、cortex-m-rt、no_std 等嵌入式库
- **置信度**: 基础 0.65 + n * 0.1, max 0.95
- **标签**: domain:embedded, lang:rust, runtime:no_std, lib:xxx

#### rust-web
- **检测规则**: 
  - 项目包含 Rust 语言文件
  - 出现 actix-web、axum、rocket、warp、hyper 等 Web 框架
- **置信度**: 基础 0.6 + n * 0.1, max 0.9
- **标签**: domain:web-backend, lang:rust, runtime:native, lib:xxx

### Java Profiles

#### java-web
- **检测规则**: 
  - 项目包含 Java 语言文件
  - 出现 jakarta.servlet、spring-core、spring-web、spring-boot 等 Web 框架
- **置信度**: 基础 0.6 + n * 0.1, max 0.9
- **标签**: domain:web-backend, lang:java, runtime:jvm, lib:xxx

#### java-lib
- **检测规则**: 
  - 项目包含 Java 语言文件
  - 出现 java.lang、java.util、java.io 等标准库
  - 多单元项目 (>5 units)
- **置信度**: 固定 0.45
- **标签**: domain:library, lang:java, runtime:jvm

## Profile 输出示例

### Python ML Project
```xml
<profiles>
  active: ml-python

  ml-python:
    confidence: 0.92
    tags:
      - domain:ml
      - runtime:cpython
      - stack:ml-python
      - lib:numpy
      - lib:torch
</profiles>
```

### System C Project
```xml
<profiles>
  active: system-c

  system-c:
    confidence: 0.80
    tags:
      - domain:system
      - lang:c
      - runtime:native
    signals:
      - multi-unit
      - kernel-layout
</profiles>
```

### Rust Embedded Project
```xml
<profiles>
  active: rust-embedded

  rust-embedded:
    confidence: 0.75
    tags:
      - domain:embedded
      - lang:rust
      - runtime:no_std
      - lib:embedded-hal
      - lib:cortex-m-rt
</profiles>
```

## 设计原则

1. **Profile 是推断结果，不是声明**
   - 不要求用户写 profile
   - 不破坏 IR 的确定性
   - profile 是 derived metadata

2. **以 canonical dependency target 为唯一输入**
   - profile 只吃已经 canonicalized 的依赖
   - profile ≠ parser

3. **confidence + tags + signals**
   - confidence: 机器可排序
   - tags: 人和下游系统可用
   - signals: debug / explainability

## 扩展指南

### 添加新的 Profile

1. 在 `core/profile_canon.py` 中定义规则集：

```python
NEW_PROFILE_LIBS = {
    "lib1", "lib2", "lib3"
}
```

2. 实现检测方法：

```python
def _detect_new_profile(self, targets: Set[str], model) -> Optional[Dict]:
    # 检测逻辑
    if not (NEW_PROFILE_LIBS & targets):
        return None

    confidence = 0.5 + min(len(found) * 0.1, 0.4)

    result = {
        "confidence": round(confidence, 2),
        "tags": [
            "domain:xxx",
            "lang:yyy",
        ]
    }

    # 可选：添加信号
    if some_condition:
        result["signals"] = ["signal1", "signal2"]

    return result
```

3. 在 `ProfileCanonicalizer.__init__` 中注册：

```python
self.rules = {
    "new-profile": self._detect_new_profile,
}
```

## 未来方向

- Profile 冲突与组合模型（ml-python + web-api）
- Profile → toolchain mapping（直接推 gcc / cargo / mvn）
- Profile fingerprint（用于缓存、增量分析、变更影响）
