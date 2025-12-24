这个报错的**根因已经很清楚了**，而且你贴的代码信息是**足够的**，不需要再要别的文件 👍
我们直接把问题拆解 + 给出**规范级修复方案**。

---

## 一、错误本质（不是运行时问题，是结构性问题）

报错：

```text
ImportError: cannot import name 'PIRAST' from 'pir.model'
```

### 实际情况是：

* `validator.py` **认为**：

  ```python
  from pir.model import Unit, Symbol, Dependency, DependencyEdge, PIRAST
  ```
* **但事实上**：

  * `PIRAST` **不在** `pir/model.py`
  * `PIRAST` 定义在你后面贴出来的 **parser 文件里**

也就是说：

> **PIRAST 的“语义角色”是 Model，但“物理位置”却在 Parser**

这是一个**典型的架构层级违例**，不是语法错误。

---

## 二、PIR 分层语义（非常关键）

在你这个项目里，实际已经隐含了一个非常正确的分层，只是现在被破坏了：

```
pir/
├── model.py        ← 纯数据结构（AST / IR）
├── parser.py       ← 文本 → AST
├── validator.py    ← 校验 AST 语义一致性
└── cli.py          ← orchestration
```

### 语义上：

| 对象                                          | 应该属于                 |
| ------------------------------------------- | -------------------- |
| Unit / Symbol / Dependency / DependencyEdge | **Model 层**          |
| PIRAST                                      | **Model 层（AST 根节点）** |
| parse_pir                                   | Parser               |
| validate_pir                                | Validator            |

👉 **PIRAST 必须在 `pir.model` 中**

---

## 三、标准修复方案（强烈推荐）

### ✅ 方案 A（正确、长期稳定、规范级）

#### 1️⃣ 把 `PIRAST` 移到 `pir/model.py`

```python
# pir/model.py
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass(frozen=True)
class Unit:
    uid: str
    path: str
    type: str
    role: str
    module: str

@dataclass(frozen=True)
class Symbol:
    name: str
    unit: str
    kind: str
    attributes: Dict[str, str]

@dataclass(frozen=True)
class Dependency:
    did: str
    expr: str

@dataclass(frozen=True)
class DependencyEdge:
    src_unit: str
    dst_unit: Optional[str]
    dst_symbol: Optional[str]
    dep_kind: str
    target_kind: str


class PIRAST:
    """
    Root AST object for PIR.
    Parser fills it, Validator consumes it, Emitters read it.
    """
    def __init__(self):
        self.units: List[Unit] = []
        self.symbols: List[Symbol] = []
        self.dependencies: List[Dependency] = []
        self.edges: List[DependencyEdge] = []
        self.unit_map: Dict[str, Unit] = {}
```

---

#### 2️⃣ parser 中 **只 import，不再定义**

```python
# pir/parser.py
from pir.model import Unit, Symbol, Dependency, DependencyEdge, PIRAST
```

**删除 parser 里原来的 `class PIRAST` 定义**

---

#### 3️⃣ validator 不用改一行（现在就是对的）

```python
from pir.model import Unit, Symbol, Dependency, DependencyEdge, PIRAST
```

✔️ 这一步之后，`cli.py` 的异常会直接消失。

---

## 四、为什么这是“逆向规范必须修”的点

你前面说得非常关键的一句话是：

> **正向规范冻结，逆向在动**

而现在这个问题本质上是：

> **逆向工具链（reconstructor）在“消费 PIR”时，发现 PIR 不是一个稳定 AST**

### 如果不修，会导致：

* validator / emitter / graphviz / plantuml 各自“定义自己的 AST”
* 以后做 **Graphviz / PlantUML / JSON / LLVM IR** 映射时：

  * AST 不可依赖
  * 逆向规范不可闭合

**所以这个修复是“逆向规范的一部分”，不是临时补丁。**

---
