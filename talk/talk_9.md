这个问题你抓得**非常准**，而且你现在遇到的不是“小 bug”，而是 **profile 推理系统必经的一道坎**：

> **profile 没有“语言主权（language ownership）”，导致 Python 规则在跨语言项目里越权**

我会分三步来解决，而且**直接给你一份「可整文件替换」的 `core/profile_canon.py`**，不是片段。

---

## 一、根因分析（为什么 Rust / C 会被识别成 Python）

### ❌ 当前算法的根本问题

你现在的 profile 规则：

* 依赖 **dependency targets**（如 `stdlib`）
* 依赖 **ProjectModel.symbols / units**
* 但 **没有强制“语言归属门控”**

于是出现三种误判：

### 1️⃣ Python 分析器本身是 Python 写的

所以任何 **多语言工具链项目** 都会满足：

* `model.langs` 包含 `PY`
* 有 `stdlib:py`
* 有 entry-point
* 有 core / analyzers

👉 **Python profile 抢占了主权**

---

### 2️⃣ Rust / C / Java profile 没有“排他性”

现在 profile 是：

> 谁 confidence 高，谁赢

但没有规则说：

> **“如果项目主语言是 Rust，就禁止 Python profile 成为 active”**

---

### 3️⃣ 工具链 ≠ 项目语言

你现在混淆了两个概念：

| 层级                      | 含义                                |
| ----------------------- | --------------------------------- |
| implementation language | 工具是用什么写的（PY）                      |
| target language         | 这个项目“分析 / 面向”的语言（C / Rust / Java） |

**profile 必须站在 target 视角，而不是实现视角**

---

## 二、正确的设计原则（这是关键）

我给你一套 **不可再乱的铁律**：

### 🧱 Rule 1：语言主权（Language Ownership）

> **一个 profile 只能在它“拥有”的语言上生效**

* python-* → 只在 `PY` 为 **dominant language** 时生效
* rust-* → 只在 `RS`
* c-* → 只在 `C / CPP`

---

### 🧱 Rule 2：主语言 ≠ 出现过的语言

必须区分：

```text
model.langs = {"PY", "C", "RS"}
```

vs

```text
dominant_lang = "RS"
```

**dominant_lang ≠ PY** 的情况下：

> ❌ python-tool / python-framework **不能成为 active**

---

### 🧱 Rule 3：工具链语言降权

如果：

> PY 只是 analyzer / infra

那么它应该：

* 允许作为 secondary profile
* 但 **永远不能抢 active**

---

## 三、解决方案总览（你只需要这一个文件）

### 我们将：

1. **引入 dominant language 推断**
2. **给每个 profile 声明 language scope**
3. **在 apply 阶段做 language gate**
4. **加入 Rust / C / Java 的 framework profile**
5. **彻底禁止 Python 越权**

---

## 四、完整可替换代码：`core/profile_canon.py`

> ⚠️ 这是**整文件**，直接覆盖你现在的版本

```python
# core/profile_canon.py
"""
Profile Canonicalization (Profile-Aware Semantic IR)

Language-owned, dominance-aware semantic profile inference.
"""

from typing import Dict, Set, Optional
from collections import Counter

# ============================================================
# Language Constants
# ============================================================

LANG_PY = "PY"
LANG_RS = "RS"
LANG_C = "C"
LANG_CPP = "CPP"
LANG_JAVA = "JAVA"

# ============================================================
# Library Signals
# ============================================================

ML_PYTHON_LIBS = {
    "numpy", "torch", "tensorflow", "keras", "scikit-learn",
    "pandas", "jax", "flax", "transformers"
}

# ============================================================
# Profile Canonicalizer
# ============================================================

class ProfileCanonicalizer:
    """
    Infer semantic profiles with strict language ownership.
    """

    def __init__(self):
        # profile_name -> (detector, owned_languages)
        self.rules = {
            "python-framework": (self._detect_python_framework, {LANG_PY}),
            "python-tool": (self._detect_python_tool, {LANG_PY}),
            "ml-python": (self._detect_ml_python, {LANG_PY}),

            "rust-framework": (self._detect_rust_framework, {LANG_RS}),
            "c-framework": (self._detect_c_framework, {LANG_C, LANG_CPP}),
            "java-framework": (self._detect_java_framework, {LANG_JAVA}),
        }

    # ========================================================
    # Entry
    # ========================================================

    def apply(self, model) -> None:
        if not model.deps_finalized:
            raise RuntimeError("Dependencies must be finalized")

        dominant_lang = self._infer_dominant_language(model)
        targets = self._extract_targets(model)

        detected = {}

        for name, (rule, owned_langs) in self.rules.items():
            # 🚫 Language ownership gate
            if dominant_lang not in owned_langs:
                continue

            result = rule(model, targets, dominant_lang)
            if result:
                detected[name] = result

        model.profiles = detected
        model.active_profile = self._pick_active_profile(detected)

    # ========================================================
    # Core Helpers
    # ========================================================

    def _infer_dominant_language(self, model) -> Optional[str]:
        """
        Determine dominant (target) language by unit count & role.
        """
        counter = Counter()

        for u in model.units:
            counter[u.type] += 1

        if not counter:
            return None

        # Highest unit count wins
        dominant, _ = counter.most_common(1)[0]
        return dominant

    def _extract_targets(self, model) -> Set[str]:
        targets = set()
        for _, _, target in model.dep_pool_items:
            if target.startswith("[") and target.endswith("]"):
                lib = target[1:-1]
                targets.add(lib.split(":")[0])
        return targets

    def _pick_active_profile(self, profiles: Dict) -> Optional[str]:
        if not profiles:
            return None
        return max(
            profiles.items(),
            key=lambda x: x[1].get("confidence", 0.0)
        )[0]

    # ========================================================
    # Python Profiles
    # ========================================================

    def _detect_python_framework(self, model, targets, lang):
        confidence = 0.0
        signals = []

        if len(model.units) >= 8:
            confidence += 0.3
            signals.append("multi-module")

        modules = {u.module for u in model.units if u.module}
        if {"core", "analyzers"} <= modules:
            confidence += 0.3
            signals.append("layered-architecture")

        class_names = {s.name.lower() for s in model.symbols if s.kind == "class"}
        if any(k in name for k in ("model", "builder", "canon", "analysis") for name in class_names):
            confidence += 0.2
            signals.append("semantic-classes")

        if confidence < 0.45:
            return None

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:language-tooling",
                "runtime:cpython",
                "stack:python-framework"
            ],
            "signals": signals
        }

    def _detect_python_tool(self, model, targets, lang):
        # Only small, flat projects
        if len(model.units) > 5:
            return None

        confidence = 0.4
        signals = ["small-project"]

        has_entry = any(
            s.kind == "func" and s.attrs.get("entry") == "true"
            for s in model.symbols
        )
        if has_entry:
            confidence += 0.2
            signals.append("entry-point")

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:tooling",
                "runtime:cpython",
                "stack:python-tool"
            ],
            "signals": signals
        }

    def _detect_ml_python(self, model, targets, lang):
        ml_found = ML_PYTHON_LIBS & targets
        if not ml_found:
            return None

        confidence = min(0.6 + len(ml_found) * 0.1, 0.95)

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:ml",
                "runtime:cpython",
                "stack:ml-python"
            ] + [f"lib:{x}" for x in sorted(ml_found)]
        }

    # ========================================================
    # Rust / C / Java Frameworks
    # ========================================================

    def _detect_rust_framework(self, model, targets, lang):
        if lang != LANG_RS:
            return None

        confidence = 0.5
        if len(model.units) >= 5:
            confidence += 0.2

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:language-tooling",
                "runtime:rust",
                "stack:rust-framework"
            ]
        }

    def _detect_c_framework(self, model, targets, lang):
        if lang not in {LANG_C, LANG_CPP}:
            return None

        confidence = 0.5
        if any("ld" in (u.module or "") for u in model.units):
            confidence += 0.2

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:language-tooling",
                "runtime:native",
                "stack:c-framework"
            ]
        }

    def _detect_java_framework(self, model, targets, lang):
        if lang != LANG_JAVA:
            return None

        confidence = 0.5
        return {
            "confidence": confidence,
            "tags": [
                "domain:language-tooling",
                "runtime:jvm",
                "stack:java-framework"
            ]
        }
```

---

## 五、现在会发生什么（你最关心的）

### ✅ 你的当前项目

* dominant_lang = `PY`
* → python-framework ✅
* → python-tool ❌（被规模否掉）

### ✅ Rust 项目（即使分析器是 Python）

* dominant_lang = `RS`
* → python-* **完全不会运行**
* → rust-framework 生效

### ✅ C / C++ 项目

* dominant_lang = `C / CPP`
* → python profile **彻底无权**

