太好了，这一步已经把 **PIR 从“语言无关 IR”推进到“语义可推理 IR”** 了 👍
你现在这份 `ProfileCanonicalizer` 写得**非常专业**，我们只需要 **按同一设计哲学补齐 C / Rust / Java**，而不是推翻重来。

下面我会做三件事：

1. **先给出设计原则（为什么这样做）**
2. **补齐 C / Rust / Java 的 profile 规则与 detector**
3. **给你一份「可直接合并」的完整代码补丁结构**

---

## 一、设计原则（和你现有 Python 方案保持一致）

你已经隐含了几个非常正确的原则：

### ✅ Profile 是「推断结果」，不是声明

* 不要求用户写 profile
* 不破坏 IR 的确定性
* profile 是 **derived metadata**

### ✅ 以「canonical dependency target」为唯一输入

你用的是：

```text
[stdlib:c]
[libc]
[newlib]
[std]
[java.lang]
[jakarta.servlet]
```

这是对的，因为：

* profile ≠ parser
* profile 只吃 **已经 canonicalized 的依赖**

### ✅ confidence + tags + signals

这是杀器级设计：

* confidence：机器可排序
* tags：人和下游系统可用
* signals：debug / explainability

👉 **下面的 C / Rust / Java 都完全遵循这一套**

---

## 二、先定义规则集（和 Python 同一层级）

### 1️⃣ C / OS / Embedded 相关

```python
# -------------------------
# C / System Profile Rules
# -------------------------

C_STDLIB_TARGETS = {
    "stdlib",   # stdlib:c
    "libc",
}

EMBEDDED_C_LIBS = {
    "newlib",
    "musl",
    "uclibc",
    "freertos",
    "zephyr",
}

KERNEL_C_SIGNALS = {
    "arch",
    "mm",
    "sched",
    "irq",
}
```

---

### 2️⃣ Rust Profile

```python
# -------------------------
# Rust Profile Rules
# -------------------------

RUST_STDLIB_TARGETS = {
    "std",
    "core",
    "alloc",
}

RUST_EMBEDDED_LIBS = {
    "riscv-rt",
    "embedded-hal",
    "cortex-m-rt",
    "no_std",
}

RUST_WEB_LIBS = {
    "actix-web",
    "axum",
    "rocket",
    "warp",
    "hyper",
}
```

---

### 3️⃣ Java Profile

```python
# -------------------------
# Java Profile Rules
# -------------------------

JAVA_STDLIB_TARGETS = {
    "java.lang",
    "java.util",
    "java.io",
}

JAVA_WEB_LIBS = {
    "jakarta.servlet",
    "spring-core",
    "spring-web",
    "spring-boot",
}

JAVA_BUILD_TOOLS = {
    "maven",
    "gradle",
}
```

---

## 三、在 `__init__` 里注册新 profile

```python
def __init__(self):
    self.rules = {
        # Python
        "ml-python": self._detect_ml_python,
        "python-tool": self._detect_python_tool,

        # C
        "system-c": self._detect_system_c,
        "embedded-c": self._detect_embedded_c,

        # Rust
        "rust-embedded": self._detect_rust_embedded,
        "rust-web": self._detect_rust_web,

        # Java
        "java-web": self._detect_java_web,
        "java-lib": self._detect_java_lib,
    }
```

---

## 四、Detector 实现（重点）

### ✅ C：system-c（偏 OS / kernel）

```python
def _detect_system_c(self, targets: Set[str], model) -> Optional[Dict]:
    if "C" not in model.langs:
        return None

    if not (C_STDLIB_TARGETS & targets):
        return None

    confidence = 0.4
    signals = []

    # 多单元加分
    if len(model.units) > 10:
        confidence += 0.15
        signals.append("multi-unit")

    # 目录语义信号
    unit_names = {u.name.lower() for u in model.units}
    if KERNEL_C_SIGNALS & unit_names:
        confidence += 0.25
        signals.append("kernel-layout")

    confidence = min(confidence, 0.9)

    return {
        "confidence": round(confidence, 2),
        "tags": [
            "domain:system",
            "lang:c",
            "runtime:native",
        ],
        "signals": signals
    }
```

---

### ✅ C：embedded-c（newlib / RTOS）

```python
def _detect_embedded_c(self, targets: Set[str], model) -> Optional[Dict]:
    embedded = EMBEDDED_C_LIBS & targets
    if not embedded:
        return None

    confidence = 0.6 + min(len(embedded) * 0.1, 0.3)

    return {
        "confidence": round(confidence, 2),
        "tags": [
            "domain:embedded",
            "lang:c",
            "runtime:baremetal",
        ] + [f"lib:{lib}" for lib in sorted(embedded)]
    }
```

---

### ✅ Rust：embedded / no_std

```python
def _detect_rust_embedded(self, targets: Set[str], model) -> Optional[Dict]:
    if "RUST" not in model.langs:
        return None

    embedded = RUST_EMBEDDED_LIBS & targets
    if not embedded:
        return None

    confidence = 0.65 + min(len(embedded) * 0.1, 0.3)

    return {
        "confidence": round(confidence, 2),
        "tags": [
            "domain:embedded",
            "lang:rust",
            "runtime:no_std",
        ] + [f"lib:{lib}" for lib in sorted(embedded)]
    }
```

---

### ✅ Rust：web backend

```python
def _detect_rust_web(self, targets: Set[str], model) -> Optional[Dict]:
    web = RUST_WEB_LIBS & targets
    if not web:
        return None

    confidence = 0.6 + min(len(web) * 0.1, 0.3)

    return {
        "confidence": round(confidence, 2),
        "tags": [
            "domain:web-backend",
            "lang:rust",
            "runtime:native",
        ] + [f"lib:{lib}" for lib in sorted(web)]
    }
```

---

### ✅ Java：web backend（Spring / Jakarta）

```python
def _detect_java_web(self, targets: Set[str], model) -> Optional[Dict]:
    if "JAVA" not in model.langs:
        return None

    web = JAVA_WEB_LIBS & targets
    if not web:
        return None

    confidence = 0.6 + min(len(web) * 0.1, 0.3)

    return {
        "confidence": round(confidence, 2),
        "tags": [
            "domain:web-backend",
            "lang:java",
            "runtime:jvm",
        ] + [f"lib:{lib}" for lib in sorted(web)]
    }
```

---

### ✅ Java：library / utility

```python
def _detect_java_lib(self, targets: Set[str], model) -> Optional[Dict]:
    if "JAVA" not in model.langs:
        return None

    if JAVA_STDLIB_TARGETS & targets and len(model.units) > 5:
        return {
            "confidence": 0.45,
            "tags": [
                "domain:library",
                "lang:java",
                "runtime:jvm",
            ]
        }

    return None
```

---

## 五、结果是什么级别？

做完这一步，你的 PIR 就具备了：

* **语言无关结构**
* **依赖 canonicalization**
* **profile-aware semantic lift**
* **confidence-ranked interpretation**

👉 这已经是：

> *“可以被 LLM、IDE、build system、code intelligence 平台 复用的 IR”*

---

## 下一步（如果你愿意）

我可以继续帮你做三件「真·工业级」的事之一：

1. **Profile 冲突与组合模型**（ml-python + web-api）
2. **Profile → toolchain mapping**（直接推 gcc / cargo / mvn）
3. **Profile fingerprint**（用于缓存、增量分析、变更影响）

你选一个，我直接往下写。
