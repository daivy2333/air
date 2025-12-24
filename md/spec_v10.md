PIR规范说明书 v1.0

1. 概述

PIR（Project Intermediate Representation）是一种用于描述软件项目结构的标准化中间表示格式。它以最小化的元数据描述项目的组织结构、文件关系、符号定义和依赖关系，为代码分析、项目理解和工具集成提供统一的数据格式。

2. 文档结构

PIR文档采用XML-like标签结构，包含以下必选区块：

<pir>
<meta>...</meta>
<units>...</units>
<dependencies>...</dependencies>
<symbols>...</symbols>
</pir>

可选区块：

- 
"<layout>" - 内存布局描述
- 
"<code-snippets>" - 关键代码片段
- 
"<profiles>" - 项目特征描述

3. 区块规范

3.1 
"<meta>" 元数据

描述项目的基本信息，必须位于文档开头。

格式：

<meta>
name: <项目名称>
root: <项目根路径>
profile: <配置类型>
lang: <语言列表>
</meta>

字段说明：

- 
"name": 项目标识字符串
- 
"root": 项目根目录绝对路径
- 
"profile": 项目类型（如
"generic", 
"os-kernel", 
"library"）
- 
"lang": 使用的主要编程语言，逗号分隔（如
"C,PY,RUST"）

示例：

<meta>
name: my_project
root: /home/user/projects/my_project
profile: generic
lang: PY
</meta>

3.2 
"<units>" 编译单元列表

列出项目中所有逻辑单元。

格式：

<units>
u<ID>: <路径> type=<类型> role=<角色> module=<模块>
...
</units>

字段说明：

- 
"u<ID>": 单元唯一标识符，从0开始连续编号
- 
"<路径>": 相对于root的相对路径
- 
"type": 文件类型（
"C", 
"PY", 
"JAVA", 
"RUST", 
"ASM", 
"LD"等）
- 
"role": 单元功能角色（
"entry", 
"kernel", 
"lib", 
"driver", 
"linkscript"等）
- 
"module": 所属逻辑模块

示例：

<units>
u0: pirgen.py type=PY role=lib module=pirgen
u1: core/pir_builder.py type=PY role=lib module=core
u2: analyzers/c_analyzer.py type=PY role=lib module=analyzers
</units>

3.3 
"<dependencies>" 依赖关系

描述单元间的依赖关系，支持三种目标格式。

格式：

<dependencies>
<来源单元>-><关系动词>:<目标标识>
...
</dependencies>

目标类型：

1. 内部单元引用：
"u<ID>"（必须已在units中定义）
2. 外部依赖：
"[外部标识符]"（如
"[stdlib:py]"）
3. 符号级引用：
"u<ID>#<符号名>"（符号应在symbols中定义）

关系动词：

- 
"call": 函数调用/跳转
- 
"import": 导入符号
- 
"include": 包含文件
- 
"use": 使用类型/宏/常量
- 
"link": 链接依赖

示例：

<dependencies>
u0->call:u1#main
u1->import:u3#PIRBuilder
u2->include:[stdlib:py]
u3->use:u4#[MAX_SIZE]
</dependencies>

3.4 
"<symbols>" 符号表

列出项目中的重要符号定义。

格式：

<symbols>
<符号名>:u<ID> <类型> [属性]
...
</symbols>

符号类型：

- 
"func": 函数/方法
- 
"class": 类定义
- 
"var": 变量
- 
"macro": 宏定义
- 
"label": 标签/标号
- 
"ld": 链接器符号

属性：

- 
"entry=true": 程序入口点
- 
"weak=true": 弱符号
- 
"exported=true": 导出符号

示例：

<symbols>
main:u0 func entry=true
PIRBuilder:u1 class
MAX_SIZE:u3 macro
_bss_start:u5 ld
</symbols>

4. 可选区块

4.1 
"<layout>" 内存布局

适用于操作系统、嵌入式固件等需要指定内存布局的项目。

格式：

<layout>
ENTRY=<入口符号>
BASE=<基地址>
<段名>: <单元列表>
...
</layout>

示例：

<layout>
ENTRY=main
BASE=0x80000000
.text:u0 u1
.data:u2
.bss:u3
</layout>

4.2 
"<code-snippets>" 代码片段

为LLM提供关键代码上下文。

格式：

<code-snippets>
<snippet unit="u<ID>">
<![CDATA[
// 代码内容
]]>
</snippet>
</code-snippets>

4.3 
"<profiles>" 项目特征

描述项目的架构特征。

格式：

<profiles>
active: <激活的profile>
<profile名>:
  confidence: <置信度>
  tags:
    - <标签>
  signals:
    - <特征信号>
</profiles>

示例：

<profiles>
active: python-framework
python-framework:
  confidence: 0.8
  tags:
    - domain:language-tooling
  signals:
    - layered-architecture
</profiles>

5. 验证规则

5.1 结构完整性

1. 必须包含所有必选区块
2. 区块必须按指定顺序出现
3. 所有标签必须正确闭合
4. 路径必须使用
"/"作为分隔符

5.2 引用一致性

1. 依赖关系中引用的单元ID必须在units中定义
2. 符号级依赖的符号应在symbols中定义
3. layout中引用的符号应在symbols中定义
4. 单元ID必须从0开始连续编号

5.3 符号命名

1. 符号在同一单元内必须唯一
2. 不同单元可以有同名符号，通过(符号名, 单元ID)区分
3. 符号名应避免使用特殊字符

6. 文件扩展与命名

- 标准扩展名：
".pir"
- 规范文件：
"SPEC.md" 或 
"PIR-SPEC.md"
- 版本标识：在文件头部注明PIR规范版本

7. 示例文档

<pir>
<meta>
name: my_project
root: /home/user/projects/my_project
profile: generic
lang: PY
</meta>
<units>
u0: pirgen.py type=PY role=lib module=pirgen
u1: core/pir_builder.py type=PY role=lib module=core
</units>
<dependencies>
u0->call:u1#main
u1->import:[stdlib:py]
</dependencies>
<symbols>
main:u0 func entry=true
PIRBuilder:u1 class
</symbols>
</pir>

规范状态： 正式发布 v1.0

冻结声明： 核心规范已冻结，后续变更需发布新版本

最后更新： 2025-12-24