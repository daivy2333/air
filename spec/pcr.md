
## PCR v1 — PIR Code Request Specification（AI 回复规范）

### 用途

AI 在 **PIR 信息不足以继续分析时**，必须按本规范输出代码索取请求。

---

### 文档格式（固定）

```text
<pcr>
<need>
type: ...
ref: ...
view: ...
</need>
...
</pcr>
```

* 仅允许 `<pcr>` 与 `<need>` 标签
* 禁止自然语言说明
* `<need>` 顺序即优先级

---

### `<need>` 字段

```text
type: <unit | symbol | layout | entry>
ref:  <PIR 可解析引用>
view: <view 枚举>
```

---

### type 语义

```text
unit    = PIR units 中的 u<ID>
symbol  = PIR symbols 中的 u<ID>#<symbol>
layout  = PIR layout 中的段名（如 .text .stack）
entry   = entry=true 的符号
```

---

### ref 解析顺序（冻结）

```text
1. u<ID>#<symbol>
2. u<ID>
3. layout 段名
4. symbols 中 entry=true
5. symbols 中全局唯一符号名
```

* 多义必须返回 ambiguous
* 不可解析必须返回 missing

---

### view 枚举（冻结）

```text
exist        // 是否存在
definition   // 定义位置 + 类型
api          // 导出接口签名
impl         // 实现摘要（非全文）
asm          // 汇编级摘要
summary      // 结构化语义总结
callchain    // 调用路径
```

---

### 强制约束（AI 必须遵守）

1. `ref` 必须可映射到 PIR
2. 禁止使用文件路径
3. 禁止请求 PIR 已明确给出的信息
4. 每个 `<need>` 必须可通过静态分析完成
5. 不允许自定义 view

---

### 示例（最小）

```text
<pcr>
<need>
type: unit
ref: u12
view: api
</need>
<need>
type: symbol
ref: u0#main
view: impl
</need>
<need>
type: layout
ref: .stack
view: summary
</need>
</pcr>
```

---

**状态**：v1 冻结
**兼容性**：仅依赖 PIR v1
**修改策略**：仅允许新增 PCR v2

