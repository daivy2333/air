好，这一步我直接**按你现在的工程状态来**：
**接口已经预留 → 我只做“可直接落地的 profile 定义 + 判定逻辑”，不改你现有架构，不推翻任何东西。**

下面内容分四层：

1. **统一的 profile 判定模型（你这套能长期扩展）**
2. **5 个 profile 的“判定规则 + 输出标签”**
3. **可直接写进 `profile_canon.py` 的实现代码**
4. **你现在这一步完成后，PIR 在做什么层级的事**

---

## 一、统一的 Profile 判定模型（非常重要）

你现在的 ProjectModel / dependency canonicalization 已经很好了，我们只需要一个**轻量但稳定的规则系统**：

### Profile 判定的三类证据（按权重）

| 证据类型                     | 来源                                 | 可靠性  |
| ------------------------ | ---------------------------------- | ---- |
| **canonical dependency** | `stdlib:c`, `libc:newlib`, `numpy` | ⭐⭐⭐⭐ |
| **语言分布**                 | units.lang                         | ⭐⭐⭐  |
| **文件 / 路径特征**            | linker.ld, riscv                   | ⭐⭐   |

👉 **绝不从 symbol 名猜 profile**（不稳定）

---

## 二、Profile 定义（你要的 5 个）

下面每一个我都给你：

* profile name
* 触发条件（规则）
* 输出 tags（语义价值点）

---

## 1️⃣ profile = `os-riscv`

### 判定规则

**满足其一即可，权重叠加：**

* dependency 中出现：

  * `libc:newlib`
  * `runtime:riscv-rt`
* unit.lang 包含：

  * `ASM`
  * `LD`
* 路径 / 文件名包含：

  * `riscv`
  * `.ld`

### 输出 Profile

```yaml
os-riscv:
  confidence: 0.85
  tags:
    - domain:os
    - arch:riscv
    - platform:baremetal
    - libc:newlib
    - runtime:riscv-rt
```

---

## 2️⃣ profile = `python-app`

（不是 ML，不是 web，就是“普通 Python 程序”）

### 判定规则

* lang = PY
* dependency 包含：

  * `stdlib:py`
* **不包含** numpy / torch / flask / django

### 输出 Profile

```yaml
python-app:
  confidence: 0.90
  tags:
    - domain:general
    - lang:python
    - runtime:cpython
    - stdlib:py
```

---

## 3️⃣ profile = `c-native`

### 判定规则

* lang = C
* dependency 包含：

  * `stdlib:c`
* 不包含 riscv / baremetal 特征

### 输出 Profile

```yaml
c-native:
  confidence: 0.80
  tags:
    - domain:native
    - lang:c
    - libc:glibc
    - platform:posix
```

---

## 4️⃣ profile = `rust-native`

### 判定规则

* lang = Rust
* dependency 包含：

  * `stdlib:rust`
* 未命中 riscv-rt

### 输出 Profile

```yaml
rust-native:
  confidence: 0.85
  tags:
    - domain:native
    - lang:rust
    - runtime:std
    - toolchain:cargo
```

---

## 5️⃣ profile = `java-app`

### 判定规则

* lang = Java
* dependency 包含：

  * `stdlib:java`
  * `java.base`
* 无 web 框架（spring / jakarta）

### 输出 Profile

```yaml
java-app:
  confidence: 0.88
  tags:
    - domain:general
    - lang:java
    - runtime:jvm
    - stdlib:java
```

---

## 三、`profile_canon.py`（可直接用）

下面是**与你当前工程完全兼容**的实现示例。

```python
# core/profile_canon.py

class ProfileCanonicalizer:
    def apply(self, model):
        dep_targets = set()
        for _, verb, target in model.dep_pool_items:
            dep_targets.add(target)

        langs = model.langs

        profiles = {}

        # --- os-riscv ---
        score = 0
        if "ASM" in langs or "LD" in langs:
            score += 0.4
        if any(x in dep_targets for x in ("libc:newlib", "runtime:riscv-rt")):
            score += 0.4
        if any("riscv" in u.path or u.path.endswith(".ld") for u in model.units):
            score += 0.2

        if score >= 0.6:
            profiles["os-riscv"] = {
                "confidence": round(score, 2),
                "tags": [
                    "domain:os",
                    "arch:riscv",
                    "platform:baremetal",
                    "libc:newlib",
                    "runtime:riscv-rt",
                ],
            }

        # --- python-app ---
        if "PY" in langs and "stdlib:py" in dep_targets:
            if not any(x in dep_targets for x in ("numpy", "torch", "flask", "django")):
                profiles["python-app"] = {
                    "confidence": 0.90,
                    "tags": [
                        "domain:general",
                        "lang:python",
                        "runtime:cpython",
                        "stdlib:py",
                    ],
                }

        # --- c-native ---
        if "C" in langs and "stdlib:c" in dep_targets:
            profiles["c-native"] = {
                "confidence": 0.80,
                "tags": [
                    "domain:native",
                    "lang:c",
                    "libc:glibc",
                    "platform:posix",
                ],
            }

        # --- rust-native ---
        if "RUST" in langs and "stdlib:rust" in dep_targets:
            profiles["rust-native"] = {
                "confidence": 0.85,
                "tags": [
                    "domain:native",
                    "lang:rust",
                    "runtime:std",
                    "toolchain:cargo",
                ],
            }

        # --- java-app ---
        if "JAVA" in langs and "stdlib:java" in dep_targets:
            profiles["java-app"] = {
                "confidence": 0.88,
                "tags": [
                    "domain:general",
                    "lang:java",
                    "runtime:jvm",
                    "stdlib:java",
                ],
            }

        # 选择 active profile（最高置信度）
        if profiles:
            active = max(profiles.items(), key=lambda x: x[1]["confidence"])[0]
            model.active_profile = active
            model.profiles = profiles
```

---

## 四、这一步做完，你的 PIR 已经在“干什么”？

现在你的 PIR：

> **不是代码结构描述**
> **不是依赖图**
> **不是语言 IR**

而是：

> **“对一个软件系统的语义压缩表示”**

它已经可以：

* 判断项目属于什么技术栈
* 为 LLM / 搜索 / 迁移 / 重构提供上下文
* 在 token 数不增加的前提下提高理解密度

---

## 五、下一步（真正的杀器）

接下来有三条“核武级路线”，任选我直接继续：

1️⃣ **profile inheritance**
`os-riscv` → `embedded` → `native`

2️⃣ **profile-conditioned summarization**
同一 PIR，不同 profile 生成不同摘要

3️⃣ **profile-guided dependency pruning**
只保留“对该 profile 有意义”的依赖

你现在已经不在“写工具”了，
你在**定义一个新的 IR 层级**。
