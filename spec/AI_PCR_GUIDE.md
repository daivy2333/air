# AI PCR 输出指南

## 概述

当 PIR 信息不足以继续分析时，AI 必须输出符合 PCR v1 规范的代码索取请求。

## 核心原则

1. **极简主义**: 仅输出必要的标签，禁止任何自然语言说明
2. **结构化**: 严格按照 XML 标签格式
3. **可解析**: 所有引用必须能映射到 PIR
4. **静态可分析**: 每个请求必须能通过静态分析完成

## 文档格式

```xml
<pcr>
<need>
type: ...
ref: ...
view: ...
</need>
...
</pcr>
```

## 字段说明

### type（必需）

四种类型：

1. **unit**: PIR units 中的 u<ID>
   - 示例: `type: unit`
   - 引用: `ref: u12`

2. **symbol**: PIR symbols 中的 u<ID>#<symbol>
   - 示例: `type: symbol`
   - 引用: `ref: u0#main`

3. **layout**: PIR layout 中的段名
   - 示例: `type: layout`
   - 引用: `ref: .stack`

4. **entry**: entry=true 的符号
   - 示例: `type: entry`
   - 引用: `ref: main`

### ref（必需）

PIR 可解析引用，按以下顺序解析：

1. u<ID>#<symbol> - 精确引用
2. u<ID> - 单元引用
3. layout 段名 - 布局段
4. entry=true 的符号 - 入口点
5. 全局唯一符号名 - 符号名

**注意**: 
- 禁止使用文件路径
- 必须可映射到 PIR
- 多义引用会返回 ambiguous
- 不可解析会返回 missing

### view（必需）

七种视图类型：

1. **exist** - 是否存在
   - 返回: yes/no/ambiguous

2. **definition** - 定义位置 + 类型
   - 返回: kind, unit

3. **api** - 导出接口签名
   - 返回: signatures 列表

4. **impl** - 实现摘要
   - 返回: behavior 短语列表（≤6条）

5. **asm** - 汇编级摘要
   - 返回: labels, flow

6. **summary** - 结构化语义总结
   - 返回: 键值对

7. **callchain** - 调用路径
   - 返回: path 列表

## 强制约束

1. `ref` 必须可映射到 PIR
2. 禁止使用文件路径
3. 禁止请求 PIR 已明确给出的信息
4. 每个 `<need>` 必须可通过静态分析完成
5. 不允许自定义 view
6. `<need>` 顺序即优先级

## 完整示例

### 示例 1: 基础查询

```xml
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

### 示例 2: 符号查询

```xml
<pcr>
<need>
type: symbol
ref: main
view: exist
</need>
<need>
type: symbol
ref: u5#process_data
view: definition
</need>
<need>
type: entry
ref: start
view: api
</need>
</pcr>
```

### 示例 3: 复合查询

```xml
<pcr>
<need>
type: unit
ref: u1
view: api
</need>
<need>
type: symbol
ref: u1#main
view: impl
</need>
<need>
type: symbol
ref: u16
view: definition
</need>
<need>
type: symbol
ref: PCRParser
view: api
</need>
<need>
type: symbol
ref: main
view: exist
</need>
</pcr>
```

## 常见错误

### ❌ 错误示例

1. 包含自然语言说明
```xml
<pcr>
我需要查看 u1 的 API 接口
<need>
type: unit
ref: u1
view: api
</need>
</pcr>
```

2. 使用文件路径
```xml
<pcr>
<need>
type: unit
ref: /path/to/file.py
view: api
</need>
</pcr>
```

3. 请求 PIR 已有信息
```xml
<pcr>
<need>
type: unit
ref: u1
view: exist
</need>
</pcr>
```
（如果 PIR 中已经明确列出了 u1）

4. 自定义 view
```xml
<pcr>
<need>
type: unit
ref: u1
view: details
</need>
</pcr>
```
（details 不是标准 view）

### ✅ 正确示例

1. 纯标签格式
```xml
<pcr>
<need>
type: unit
ref: u1
view: api
</need>
</pcr>
```

2. 使用 PIR 引用
```xml
<pcr>
<need>
type: unit
ref: u1
view: api
</need>
</pcr>
```

3. 请求新增信息
```xml
<pcr>
<need>
type: unit
ref: u1
view: impl
</need>
</pcr>
```
（impl 包含实现细节，PIR 中未提供）

4. 使用标准 view
```xml
<pcr>
<need>
type: unit
ref: u1
view: impl
</need>
</pcr>
```

## 最佳实践

1. **按优先级排序**: 将最重要的请求放在前面
2. **批量请求**: 一次请求多个相关信息，减少交互次数
3. **精确引用**: 优先使用 u<ID>#<symbol> 格式
4. **选择合适视图**: 根据需要选择最小视图
5. **避免重复**: 不要请求 PIR 中已有的信息

## 测试

使用以下命令测试 PCR 输出：

```bash
# 保存 PCR 到文件
echo '<pcr>...</pcr>' > request.pcr

# 使用 peek 工具处理
air peek request.pcr
```

## 参考资料

- PCR v1 规范: `/spec/pcr.md`
- PCES v1 规范: `/spec/pces.md`
- PIR v1 规范: `/spec/ir.md`
