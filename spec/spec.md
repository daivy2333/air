PIR规范说明书 v1

1. 概述

PIR（Project Intermediate Representation）是一种用于描述软件项目结构的标准化中间表示格式。它以最小化的元数据描述项目的组织结构、文件关系、符号定义和依赖关系，为代码分析、项目理解和AI辅助编程提供统一的数据格式。

设计目标：

1. AI友好 - 极简token开销，便于LLM理解
2. 语言无关 - 支持多种编程语言和项目类型
3. 分层抽象 - 从文件到符号的多层次描述
4. 高效序列化 - 紧凑的文本表示形式

2. 版本兼容性

版本 状态 变更说明
v1.0 废弃 初始规范，存在格式不一致问题
v1.1 当前 统一格式，引入依赖池优化，强化AI友好特性

3. 文档结构

PIR文档采用XML-like标签结构，包含以下区块：

3.1 必选区块

<pir>
  <meta>...</meta>                <!-- 项目元数据 -->
  <units>...</units>              <!-- 编译单元列表 -->
  <dependency-pool>...</dependency-pool> <!-- 依赖池 -->
  <dependencies>...</dependencies><!-- 单元依赖关系 -->
  <symbols>...</symbols>          <!-- 符号定义表 -->
</pir>

3.2 可选区块

<profiles>...</profiles>          <!-- 项目特征分析 -->
<layout>...</layout>              <!-- 内存布局（嵌入式/OS项目） -->
<code-snippets>...</code-snippets><!-- 关键代码片段这个是预留的目前好像还没用 -->

4. 区块规范

4.1 
"<meta>" - 项目元数据

位置： 必须位于文档开头

用途： 描述项目基本信息和上下文

格式：

<meta>
name: <项目名称>
root: <项目根路径>
profile: <配置类型>
lang: <主编程语言>
</meta>

字段说明：

- 
"name": 项目标识符（ASCII字符串，不含空格）
- 
"root": 项目根目录绝对路径（POSIX格式）
- 
"profile": 项目类型枚举
   - 
"generic" - 通用项目
   - 
"os-kernel" - 操作系统内核
   - 
"library" - 库项目
   - 
"framework" - 框架项目
   - 
"cli-tool" - 命令行工具
- 
"lang": 主编程语言代码（2-4字符大写）
   - 
"PY" - Python
   - 
"C" - C语言
   - 
"CPP" - C++
   - 
"RS" - Rust
   - 
"JAVA" - Java
   - 
"GO" - Go

示例：

<meta>
name: pirgen
root: /home/aidlux/air/pirgen
profile: cli-tool
lang: PY
</meta>

4.2 
"<units>" - 编译单元列表

用途： 列出项目中所有逻辑代码单元，建立文件到逻辑单元的映射

格式：

<units>
u<ID>: <相对路径> type=<类型> role=<角色> module=<模块>
...
</units>

字段规范：

- 
"u<ID>": 单元唯一标识符
   - 从0开始连续递增整数
   - 格式：
"u" + 十进制数字
   - 示例：
"u0", 
"u1", ..., 
"u999"
- 
"<相对路径>": 相对于root的文件系统路径
   - 使用
"/"作为路径分隔符
   - 文件名需包含扩展名
   - 示例：
"core/pir_builder.py"
- 
"type": 文件类型（大写）
   - 
"PY" - Python源文件
   - 
"C" - C源文件
   - 
"H" - C头文件
   - 
"RS" - Rust源文件
   - 
"JAVA" - Java源文件
   - 
"ASM" - 汇编文件
   - 
"LD" - 链接器脚本
   - 
"MK" - Makefile
   - 
"CONF" - 配置文件
- 
"role": 单元在项目中的功能角色
   - 
"entry" - 程序入口点
   - 
"lib" - 库代码
   - 
"kernel" - 内核代码
   - 
"driver" - 设备驱动
   - 
"test" - 测试代码
   - 
"util" - 工具代码
   - 
"config" - 配置文件
   - 
"doc" - 文档
- 
"module": 所属逻辑模块
   - 点分隔的模块路径
   - 示例：
"core", 
"analyzers.base"

验证规则：

1. ID必须连续且唯一
2. 路径必须在项目根目录下
3. 类型必须是预定义类型之一
4. 角色必须是预定义角色之一

示例：

<units>
u0: pirgen.py type=PY role=entry module=pirgen
u1: core/pir_builder.py type=PY role=lib module=core
u2: analyzers/c_analyzer.py type=PY role=lib module=analyzers
</units>

4.3 
"<dependency-pool>" - 依赖池

设计动机： 优化重复依赖项的表示，减少token开销，提高AI解析效率

格式：

<dependency-pool>
d<ID>: <依赖类型>[<目标标识符>]
...
</dependency-pool>

依赖类型：

1. 内部单元引用（直接引用）
   - 格式：
"ref:u<ID>"
   - 示例：
"d0: ref:u3"
2. 内部符号引用（符号级引用）
   - 格式：
"sym:u<ID>#<符号名>"
   - 示例：
"d1: sym:u3#ProjectModel"
3. 外部依赖引用（外部库/框架）
   - 格式：
"ext:[<命名空间>:<标识符>]"
   - 示例：
      - 
"d2: ext:[stdlib:py]"（Python标准库）
      - 
"d3: ext:[libc:stdio]"（C标准库）
      - 
"d4: ext:[pkg:requests]"（第三方包）
4. 模块导入（模块级别）
   - 格式：
"import:<模块路径>"
   - 示例：
      - 
"d5: import:analyzers"
      - 
"d6: import:core.project_model"

池化规则：

1. 相同依赖项只定义一次
2. 按首次出现顺序分配ID
3. 从0开始连续编号

示例：

<dependency-pool>
d0: ext:[stdlib:py]
d1: sym:u3#ProjectModel
d2: sym:u2#PIRBuilder
d3: import:core.analysis_cache
d4: import:core.dep_canon
d5: import:core.profile_canon
d6: import:core.project_model
d7: import:analyzers
d8: import:.c_analyzer
d9: import:.python_analyzer
</dependency-pool>

4.4 
"<dependencies>" - 单元依赖关系

用途： 描述编译单元之间的依赖关系

格式：

<dependencies>
<单元ID>-><关系动词>:[<依赖池ID列表>]
...
</dependencies>

关系动词：

- 
"import" - 导入/引用（最常用）
- 
"call" - 函数调用
- 
"extend" - 继承
- 
"implement" - 接口实现
- 
"include" - 包含文件
- 
"use" - 使用类型/宏
- 
"link" - 链接依赖

语法说明：

- 
"[d0 d1 d2]" - 方括号内的空格分隔ID列表
- 按依赖类型分组，同类型依赖放在一起
- 单个单元可有多行依赖定义

示例：

<dependencies>
u0->import:[d0 d1 d2 d3 d4 d5 d6 d7]
u7->import:[d0 d6]
u13->import:[d8 d9]
</dependencies>

4.5 
"<symbols>" - 符号定义表

用途： 记录项目中的关键符号（函数、类、变量等）

格式：

<symbols>
<符号名>:u<ID> <类型> [属性...]
...
</symbols>

符号类型：

- 
"func" - 函数/方法
- 
"class" - 类/结构体定义
- 
"var" - 变量/常量
- 
"macro" - 宏定义
- 
"label" - 标签/标号
- 
"type" - 类型定义
- 
"interface" - 接口
- 
"enum" - 枚举
- 
"trait" - 特质（Rust）

属性标记：

- 
"entry=true" - 程序入口点
- 
"exported=true" - 导出符号
- 
"public=true" - 公共可见性
- 
"private=true" - 私有可见性
- 
"static=true" - 静态符号
- 
"weak=true" - 弱符号
- 
"virtual=true" - 虚函数

命名规则：

1. 遵循源语言的命名约定
2. 同一单元内符号名唯一
3. 不同单元允许重名符号

示例：

<symbols>
main:u0 func entry=true
PIRBuilder:u2 class
Unit:u3 class
ProjectModel:u3 class
BaseAnalyzer:u7 class public=true
get_analyzer:u13 func exported=true
</symbols>

4.6 
"<profiles>" - 项目特征分析（可选）

用途： AI辅助的项目特征识别结果

格式：

<profiles>
active: <激活的profile>
<profile名>:
  confidence: <置信度>
  tags:
    - <分类>:<值>
  signals:
    - <特征信号>
</profiles>

字段说明：

- 
"active": 最匹配的项目特征
- 
"<profile名>": 特征名称（kebab-case）
- 
"confidence": 匹配置信度（0.0-1.0）
- 
"tags": 分类标签列表
- 
"signals": 识别出的特征信号

预定义特征：

python-framework:
  tags: [domain:language-tooling, runtime:cpython]
  signals: [layered-architecture, multi-module]

os-kernel:
  tags: [domain:system, arch:riscv]
  signals: [low-level, hardware-abstraction]

embedded-firmware:
  tags: [domain:embedded, constraints:memory]
  signals: [bare-metal, real-time]

示例：

<profiles>
active: python-framework
python-framework:
  confidence: 0.8
  tags:
    - domain:language-tooling
    - runtime:cpython
    - stack:python-framework
  signals:
    - layered-architecture
    - multi-module
    - semantic-classes
</profiles>

4.7 
"<layout>" - 内存布局（可选）

适用场景： 操作系统、嵌入式系统、裸机程序

格式：

<layout>
ENTRY=<入口符号>
BASE=<基地址>
<段名>: <单元ID列表>
...
</layout>

示例：

<layout>
ENTRY=main
BASE=0x80000000
.text:u0 u1 u2
.data:u3 u4
.bss:u5 u6
.vectors:u7
</layout>

4.8 
"<code-snippets>" - 关键代码片段（可选）

用途： 为LLM提供重要代码的上下文

格式：

<code-snippets>
<snippet unit="u<ID>" symbol="<符号名>">
<![CDATA[
// 代码内容
]]>
</snippet>
</code-snippets>

选择策略：

1. 入口函数
2. 核心算法
3. 复杂的数据结构
4. 关键的配置逻辑

5. 序列化规范

5.1 文本编码

- 编码: UTF-8 without BOM
- 换行: LF (
"\n")
- 缩进: 2个空格

5.2 文件命名

- 标准扩展名: 
".pir"
- 命名模式: 
"<项目名>-[<profile>].pir"
- 示例: 
"pirgen-cli-tool.pir"

5.3 验证规则

结构完整性：

1. 必须包含所有必选区块
2. 区块顺序必须符合规范
3. 所有标签必须正确闭合
4. XML格式必须良好

引用一致性：

1. 依赖引用的单元ID必须在units中定义
2. 符号引用的单元ID必须在units中定义
3. 依赖池ID必须在dependencies中引用
4. layout引用的符号必须在symbols中定义

标识符唯一性：

1. 单元ID全局唯一且连续
2. 依赖池ID全局唯一且连续
3. (符号名, 单元ID)组合唯一

8.3 文档生成

输入: project.pir
输出: 项目架构文档

1. 从units生成文件树
2. 从dependencies生成依赖图
3. 从symbols生成API文档
4. 从profiles生成项目概述

9. 性能考虑

9.1 Token优化

- 使用短标识符（
"u0", 
"d0"）
- 依赖池减少重复
- 紧凑的文本格式

9.2 解析效率

- 线性时间复杂度的解析器
- 最小化内存占用
- 流式处理支持

10. 完整示例

见附录A：典型Python项目PIR表示

附录A：典型Python项目PIR表示

<pir>
<meta>
name: pirgen
root: /home/aidlux/air/pirgen
profile: cli-tool
lang: PY
</meta>
<units>
u0: pirgen.py type=PY role=entry module=pirgen
u1: min_token.py type=PY role=util module=pirgen
u2: core/pir_builder.py type=PY role=lib module=core
u3: core/project_model.py type=PY role=lib module=core
u4: core/analysis_cache.py type=PY role=lib module=core
u5: core/dep_canon.py type=PY role=lib module=core
u6: core/profile_canon.py type=PY role=lib module=core
u7: analyzers/base.py type=PY role=lib module=analyzers
u8: analyzers/c_analyzer.py type=PY role=lib module=analyzers
u9: analyzers/rust_analyzer.py type=PY role=lib module=analyzers
u10: analyzers/java_analyzer.py type=PY role=lib module=analyzers
u11: analyzers/python_analyzer.py type=PY role=lib module=analyzers
u12: analyzers/asm_ld_analyzer.py type=PY role=lib module=analyzers
u13: analyzers/__init__.py type=PY role=lib module=analyzers
</units>
<dependency-pool>
d0: ext:[stdlib:py]
d1: sym:u3#ProjectModel
d2: sym:u2#PIRBuilder
d3: import:core.analysis_cache
d4: import:core.dep_canon
d5: import:core.profile_canon
d6: import:core.project_model
d7: import:analyzers
d8: import:.c_analyzer
d9: import:.python_analyzer
d10: import:.java_analyzer
d11: import:.rust_analyzer
d12: import:.asm_ld_analyzer
d13: import:.base
</dependency-pool>
<dependencies>
u0->import:[d0 d1 d2 d3 d4 d5 d6 d7]
u1->import:[d0]
u2->import:[d6]
u3->import:[d0]
u4->import:[d0]
u6->import:[d0]
u7->import:[d0 d6]
u8->import:[d0 d13 d6]
u9->import:[d0 d13 d6]
u10->import:[d0 d13 d6]
u11->import:[d0 d13 d6]
u12->import:[d0 d13 d6]
u13->import:[d8 d9 d10 d11 d12]
</dependencies>
<symbols>
discover_source_files:u0 func
infer_unit_meta:u0 func
scan_project:u0 func
resolve_dependencies:u0 func
main:u0 func entry=true
is_source_file:u1 func
strip_c_comments:u1 func
minify_c_style:u1 func
minify_python:u1 func
process_directory:u1 func
main:u1 func entry=true
PIRBuilder:u2 class
Unit:u3 class
Symbol:u3 class
Dependency:u3 class
ProjectModel:u3 class
AnalysisCache:u4 class
canonicalize_target:u5 func
canonicalize_dependencies:u5 func
ProfileCanonicalizer:u6 class
BaseAnalyzer:u7 class
CAnalyzer:u8 class
RustAnalyzer:u9 class
JavaAnalyzer:u10 class
PythonAnalyzer:u11 class
AsmLdAnalyzer:u12 class
get_analyzer:u13 func
</symbols>
<profiles>
active: python-framework
python-framework:
  confidence: 0.8
  tags:
    - domain:language-tooling
    - runtime:cpython
    - stack:python-framework
  signals:
    - layered-architecture
    - multi-module
    - semantic-classes
</profiles>
</pir>



规范状态： 正式发布 v1

冻结声明： 核心规范已冻结，后续变更需发布新版本

最后更新： 2025-12-24

维护者： daivy