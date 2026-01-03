# 一、PCES v1 规范（PIR Code Evidence Specification）

这是**工具输出给 AI 的规范文本**，和 PCR 一样，必须稳定、完整。

---

## 1. 定位

PCES 是 **PCR 的确定性回答**，提供**完整、准确的代码证据**。

* PCR：我需要什么
* PCES：这是需要的代码（完整保留），一个代码提取器而非分析器

PCES **不分析、不优化、不推断，只提供完整的代码信息**。

**核心原则**：
* **信息完整性优先** - 必须保留 AI 需要的所有代码信息（函数签名、类定义、变量声明等）
* **不损失语义** - 代码结构、类型信息、调用关系等必须准确保留
* **按需提供** - 仅提供 PCR 请求的代码，但提供时必须完整

---

## 2. 文档结构（固定）

```text
<pcir>
<evidence>
ref: ...
view: ...
source: ...
content:
  ...
</evidence>
...
</pcir>
```

* `<evidence>` 与 `<need>` 一一对应
* 顺序必须与 PCR 中 `<need>` 顺序一致
* 禁止多余文本
* 每个证据必须包含完整的信息，不得省略关键字段

---

## 3. `<evidence>` 字段

### 3.1 固定字段

```text
ref:    与 PCR 完全一致
view:   与 PCR 完全一致
source: u<ID> | layout | unknown
```

* `source` 是**最终证据来源**，必须准确
* layout 类证据使用 `layout`
* 所有字段必须完整提供，不得省略

---

## 4. content 规范（按 view 决定）

### 4.1 exist

```text
content:
  status: yes | no | ambiguous
  location: <位置信息>  # 当 status 为 yes 时
```

规则：

* 当 status 为 yes 时，必须提供完整的位置信息
* 位置信息应包含文件路径、行号等

---

### 4.2 definition

```text
content:
  kind: func | class | var | label | type
  unit: u<ID>
  definition: <完整定义>
```

规则：

* `definition` 必须包含完整的符号定义（包括类型、修饰符等）
* 不得省略任何关键信息

---

### 4.3 api

```text
content:
  signatures:
    - <完整签名>
    - <完整签名>
```

规则：

* 必须包含完整的函数/方法签名（名称、参数类型、返回值类型、修饰符等）
* 顺序与源码一致
* 不输出实现细节
* 保留所有类型信息和泛型参数

---

### 4.4 impl（实现详情）

```text
content:
  implementation:
    - <完整实现信息>
    - <完整实现信息>
```

规则：

* 必须保留完整的实现逻辑
* 保留关键控制流（if/else、循环、分支等）
* 保留关键操作和副作用
* 保留重要的函数调用
* 不得简化或省略关键信息

---

### 4.5 asm

```text
content:
  labels:
    - <完整标签信息>
  flow:
    - <完整步骤>
    - <完整步骤>
```

规则：

* 必须包含完整的标签信息（地址、名称等）
* 必须包含完整的控制流信息
* 不得省略关键指令

---

### 4.6 summary（结构化）

```text
content:
  <key>: <完整值>
  <key>: <完整值>
```

规则：

* 仅允许 **键值对**
* 值必须包含完整的结构化信息
* 不得省略关键字段

---

### 4.7 callchain

```text
content:
  path:
    - u<ID>#symbol
    - u<ID>#symbol
```

规则：

* 必须包含完整的调用路径
* 保留每个调用点的上下文信息
* 不得省略中间调用环节

---

## 5. 错误与缺失（冻结）

```text
content:
  status: missing
  reason: <缺失原因>  # 可选，提供完整原因
```

或

```text
content:
  status: ambiguous
  candidates: <可能的候选项>  # 可选，提供完整候选项列表
```

禁止附加无关解释。

---

## 6. 完整性约束

1. **禁止信息丢失** - 必须保留所有 AI 需要的代码信息（签名、类型、参数、返回值等）
2. **禁止输出完整文件** - 仅输出 PCR 请求的代码部分
3. **禁止输出未被 PCR 请求的符号** - 避免无关信息干扰
4. **禁止跨 `<evidence>` 重复内容** - 避免冗余
5. **content 必须为结构化文本** - 保持格式一致性
6. **每个 `<evidence>` 必须可独立理解** - 包含完整的上下文信息
7. **禁止破坏代码语义** - 不得简化或省略关键信息

---

## 7. 最小示例

```text
<pcir>
<evidence>
ref: u12
view: api
source: u12
content:
  signatures:
    - fn get_analyzer(lang: str) -> Analyzer
</content>
</evidence>
<evidence>
ref: .stack
view: summary
source: layout
content:
  top: __stack_top
  size: 0x8000
</content>
</evidence>
</pcir>
```

---

**状态**：PCES v1（建议冻结）
**依赖**：PIR v1 + PCR v1

---