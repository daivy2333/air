pirgen/
├── pirgen.py                 # 主入口：自动路由 + 配置加载
├── core/
│   ├── pir_builder.py        # PIR 文本构建器（严格按规范）
│   ├── project_model.py      # 内部数据模型（Unit, Symbol, Dep...）
│   └── dep_canon.py          # 依赖语义归一化（Dependency Canonicalization）
├── analyzers/
│   ├── base.py               # Analyzer 抽象基类
│   ├── c_analyzer.py         # C/C++（用 gcc -MM + ctags）
│   ├── rust_analyzer.py      # Rust（用 rustc --emit=dep-info + rust-analyzer）
│   ├── java_analyzer.py      # Java（用 javac -XprintRounds 或解析 imports）
│   ├── python_analyzer.py    # Python（用 ast 模块）
│   ├── asm_ld_analyzer.py    # 汇编 & 链接脚本（正则 + 启发式）
│   └── __init__.py           # 注册所有 analyzer
├── README_CANON.md           # 依赖归一化功能说明文档
└── config_schema.json        # （可选）配置文件 schema

## PIR 生成流程

1. scan_project - 扫描项目源文件
2. resolve_dependencies - 解析依赖关系
3. canonicalize_dependencies - 归一化依赖语义（新增）
4. finalize_dependencies - 最终化依赖
5. emit PIR - 生成 PIR 文件

## 依赖归一化

将标准库依赖归一化为语义形式：
- Python: [os], [sys], [re] → [stdlib:py]
- C: [stdio.h], [stdlib.h] → [stdlib:c]
- Rust: [std::xxx] → [stdlib:rust]

详见 README_CANON.md


# PIR - Project Intermediate Representation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🚀 简介
PIR是一种面向AI优化的项目中间表示，旨在用最少的token完整描述项目架构...

## ✨ 特性
- ✅ 多语言支持 (Python, Rust, C/C++, Java, 汇编等)
- ✅ 依赖关系池压缩算法
- ✅ Profile-Aware语义推断
- ✅ 极简Token设计

# 生成 PIR
python -m air forward ./my_project

# 生成架构图
python -m air reverse my_project.pir --format arch

# 生成流程图
python -m air reverse my_project.pir --format pipeline

todo:

1.文本图形化
字面意思，因为我这个规范的文本可以读取相互关系，图形化也是理所当然

2.逆向工程
字面意思，从文本读取信息，创建一个项目空壳，对我来说做到这里就够了

3.我梦到漫天的繁星，那时候你说...

PIR is an architectural-level IR, not a semantic or execution-level IR.

# 对了，请吧一下语料先喂给给ai，让他知道什么是pcr，一定要严格规范才能返回有用的pcr文件

Prompt

AI PCR输出规范 (V1版本)

🎯 核心原则

PCR输出必须严格遵守以下原则：
1. **极简主义**：仅输出XML标签，禁止任何自然语言说明
2. **结构化**：严格按照PCR v1 XML格式
3. **可解析**：所有引用必须能映射到PIR
4. **静态可分析**：每个请求必须能通过静态分析完成


📄 文档格式模板

<pcr>
<need>
type: ...
ref: ...
view: ...
</need>

</pcr>


🔤 字段定义详解 (V1版本)

type字段（必需，4种类型）

1. **unit**: 引用PIR units中的u<id>
   示例: type: unit
   引用: ref: u12

2. **symbol**: 引用PIR symbols中的u<id>#<symbol>
   示例: type: symbol
   引用: ref: u0#main

3. **entry**: 引用entry=true的符号
   示例: type: entry
   引用: ref: main
   
注意：V1版本不支持layout类型


ref字段（必需，按优先级解析）

引用解析优先级（V1）：
1. u<id>#<symbol> - 精确引用（推荐）
2. entry符号名 - 入口点
3. 全局唯一符号名 - 符号名

禁止：文件路径
要求：必须可映射到PIR
结果：多义→ambiguous，不可解析→missing


view字段（必需，V1支持的3种视图）

V1支持以下视图：

1. **exist** - 是否存在
   返回: yes/no/ambiguous
   用途：检查符号是否存在

2. **impl** - 实现摘要
   返回: 代码实现片段
   用途：查看函数/结构体/类的实现代码

3. **summary** - 结构化语义总结
   返回: 基本类型信息和单元统计
   用途：了解符号或单元的基本信息


🚫 V1版本限制

V1版本不支持以下功能：
1. ❌ api视图 - 模块接口信息
2. ❌ asm视图 - 汇编级信息
3. ❌ callchain视图 - 调用链分析
4. ❌ definition视图 - 详细定义信息
5. ❌ layout视图 - 内存布局信息
6. ❌ 文件路径引用


📋 V1完整示例集合

示例1：基础函数查询

<pcr>
<need>
type: symbol
ref: u0#main
view: impl
</need>
<need>
type: symbol
ref: Calculator
view: exist
</need>
<need>
type: unit
ref: u1
view: summary
</need>
</pcr>


示例2：入口点探索

<pcr>
<need>
type: entry
ref: main
view: exist
</need>
<need>
type: entry
ref: main
view: impl
</need>
<need>
type: symbol
ref: u7#rust_main
view: impl
</need>
</pcr>


示例3：数据结构探索

<pcr>
<need>
type: symbol
ref: AppManager
view: impl
</need>
<need>
type: symbol
ref: u17#TrapContext
view: impl
</need>
<need>
type: symbol
ref: LogConfig
view: impl
</need>
</pcr>


🎯 V1最佳实践

实践1：从精确引用开始


<pcr>
<need>
type: symbol
ref: u16#greet
view: impl
</need>
<need>
type: symbol
ref: u19#greet
view: impl
</need>
</pcr>


实践2：先检查再深入


<pcr>
<need>
type: symbol
ref: panic
view: exist
</need>
<need>
type: symbol
ref: u1#panic
view: impl
</need>
</pcr>


实践3：模块级探索


<pcr>
<need>
type: unit
ref: u2
view: summary
</need>
<need>
type: symbol
ref: u2#run_next_app
view: impl
</need>
<need>
type: symbol
ref: u2#AppManager
view: impl
</need>
</pcr>


🔄 处理ambiguous的策略

策略1：探索所有可能性


<pcr>
<need>
type: symbol
ref: u3#main
view: impl
</need>
<need>
type: symbol
ref: u14#main
view: impl
</need>
<need>
type: symbol
ref: u18#main
view: impl
</need>
</pcr>


策略2：优先探索入口点


<pcr>
<need>
type: entry
ref: main
view: exist
</need>
<need>
type: entry
ref: _start
view: exist
</need>
<need>
type: symbol
ref: u5#_start
view: impl
</need>
</pcr>


❌ V1常见错误

错误1：请求不支持的功能


<pcr>
<need>
type: unit
ref: u1
view: api
</need>
</pcr>


错误2：使用layout类型


<pcr>
<need>
type: layout
ref: .stack
view: summary
</need>
</pcr>


错误3：模糊引用导致ambiguous


<pcr>
<need>
type: symbol
ref: main
view: impl
</need>
</pcr>

<pcr>
<need>
type: symbol
ref: u3#main
view: impl
</need>
</pcr>


✅ V1正确模式

模式1：探索函数实现

<pcr>
<need>
type: symbol
ref: u21#add
view: impl
</need>
<need>
type: symbol
ref: u17#add
view: impl
</need>
</pcr>


模式2：分析结构体定义

<pcr>
<need>
type: symbol
ref: u2#AppManager
view: impl
</need>
<need>
type: symbol
ref: u17#TrapContext
view: impl
</need>
<need>
type: symbol
ref: u20#UPSafeCell
view: impl
</need>
</pcr>


模式3：验证符号存在

<pcr>
<need>
type: symbol
ref: shutdown
view: exist
</need>
<need>
type: symbol
ref: clear_bss
view: exist
</need>
<need>
type: symbol
ref: u4#shutdown
view: impl
</need>
</pcr>


💡 AI工作流提示

提示1：从PIR开始


"分析PIR，找到感兴趣的函数或结构体，使用精确引用请求impl视图。"


提示2：处理多义性


"如果符号在多个模块中存在，先检查exist视图，然后分别用精确引用探索。"


提示3：渐进探索


"从入口点开始，根据代码调用关系逐步深入探索被调用的函数。"


🎯 V1版本AI检查清单

AI输出PCR前检查（V1）：
[ ] 1. 是否纯XML格式，无自然语言
[ ] 2. 只使用V1支持的type：unit/symbol/entry
[ ] 3. 只使用V1支持的view：exist/impl/summary
[ ] 4. 优先使用精确引用（u<id>#<symbol>）
[ ] 5. 不使用文件路径
[ ] 6. 不请求api/asm/callchain/definition/layout视图
[ ] 7. 按优先级排序<need>
[ ] 8. 每个请求都可静态分析


📁 V2版本规划功能

计划在V2版本添加：
1. ✅ api视图 - 模块接口信息
2. ✅ asm视图 - 汇编级分析
3. ✅ callchain视图 - 调用链跟踪
4. ✅ definition视图 - 详细定义
5. ✅ layout视图 - 内存布局
6. ✅ 更智能的ambiguous处理
7. ✅ 代码片段上下文扩展