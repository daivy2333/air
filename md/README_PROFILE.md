# PIR v0.4 - Profile-Aware Semantic IR

## 概述

PIR v0.4 引入了 **profile-aware canonicalization**，这是一个向后兼容的扩展，为 PIR 添加了高层语义理解能力。

### 核心概念

**Profile** 是对项目的高层语义解释，通过分析依赖模式、文件结构和可选的用户提示来推断得出。

Profile 是非权威的、派生的元数据，与 dependency（依赖关系）区分开来：

- **Dependency** = "代码关系"
- **Profile** = "语义理解"

## Profile Spec

### XML 结构

```xml
<profiles>
  active: ml-python

  ml-python:
    confidence: 0.92
    tags:
      - domain:ml
      - runtime:cpython
      - stack:ml-python
      - lib:torch
      - lib:numpy

  os-riscv:
    confidence: 0.41
    tags:
      - platform:baremetal
      - runtime:riscv-rt
</profiles>
```

### 关键语义

| 概念                | 说明                    |
| ----------------- | --------------------- |
| `profiles.active` | 当前主 profile（只能一个）     |
| `confidence`      | 推断置信度（0~1）            |
| `tags`            | 语义标签集合                |
| 多 profile         | **允许共存，但只有一个 active** |

## 实现细节

### ProjectModel 扩展

```python
class ProjectModel:
    def __init__(self, name: str, root: str, profile: str):
        # ...

        # ---- Profiles (v0.4 extension) ----
        self.profiles: Dict[str, Dict] = {}  # profile_name -> {confidence, tags}
        self.active_profile: Optional[str] = None  # Current active profile
```

### ProfileCanonicalizer

```python
class ProfileCanonicalizer:
    def apply(self, model):
        # 读取 model.dependencies / units / files
        # 推断 profile
        model.active_profile = "ml-python"
        model.profiles["ml-python"] = {
            "confidence": 0.92,
            "tags": [...]
        }
```

### 调用位置

在 `pirgen.py` 中：

```python
model.resolve_dependencies()
canonicalize_dependencies(model)
model.finalize_dependencies()

# Apply profile-aware canonicalization (v0.4)
ProfileCanonicalizer().apply(model)

builder = PIRBuilder(model)
```

## 当前支持的 Profile

### ml-python

判断规则：
- 出现 `numpy` / `torch` / `tensorflow` 等 ML 库
- 置信度基于检测到的 ML 库数量计算
- 自动生成标签：`domain:ml`, `runtime:cpython`, `stack:ml-python`, `lib:xxx`

## 扩展指南

### 添加新的 Profile

1. 在 `core/profile_canon.py` 中定义规则：

```python
NEW_PROFILE_LIBS = {
    "lib1", "lib2", "lib3"
}

def _detect_new_profile(self, targets: Set[str], model) -> Optional[Dict]:
    # 实现检测逻辑
    # 返回 {confidence, tags} 或 None
```

2. 在 `ProfileCanonicalizer.__init__` 中注册：

```python
self.rules = {
    "ml-python": self._detect_ml_python,
    "new-profile": self._detect_new_profile,
}
```

## 向后兼容性

PIR v0.4 完全向后兼容：

- ✅ 不修改已有 `<dependency-pool>`
- ✅ 不修改 `<dependencies>`
- ✅ 不污染 `<symbols>`
- ✅ 保留旧的 `profile` 字段（标记为 legacy）

## 示例

### 原始 PIR (v0.3)

```xml
<pir>
<meta>
name: my_project
root: /path/to/project
profile: generic
lang: PY
</meta>
<units>...</units>
<dependency-pool>...</dependency-pool>
<dependencies>...</dependencies>
<symbols>...</symbols>
</pir>
```

### 增强 PIR (v0.4)

```xml
<pir>
<meta>
name: my_project
root: /path/to/project
profile: generic
lang: PY
</meta>
<units>...</units>
<dependency-pool>...</dependency-pool>
<dependencies>...</dependencies>
<symbols>...</symbols>
<profiles>
  active: ml-python

  ml-python:
    confidence: 0.92
    tags:
      - domain:ml
      - runtime:cpython
      - stack:ml-python
      - lib:torch
      - lib:numpy
</profiles>
</pir>
```

## 设计原则

1. **PIR v0.x 向后兼容**
2. **profile 是"派生语义"，不是源码事实**
3. **profile ≠ dependency**

## 未来方向

- 多 profile 继承
- Profile 置信度阈值配置
- 用户声明的 profile 提示
- 更丰富的 profile taxonomy（domain / runtime / stack）
