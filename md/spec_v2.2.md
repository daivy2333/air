PIR: Project Intermediate Representation (项目中间表示) 规范

版本号： v0.2.1

文档状态： 核心规范冻结 (Stable Core)

发布日期： 2025-12-23

起草者： PIR Design Team（only daivy in 2025）

版权声明： © 2025 PIR Design Team. 本文档内容可根据MIT开源协议或CC0协议自由使用、分发与修改。

1. 摘要

PIR（Project Intermediate Representation）是一种面向软件项目的轻量级中间表示格式。其设计目标在于以极简的符号（Token）成本，精确描述项目的核心结构、模块依赖关系及关键语义信息。PIR主要服务于静态代码分析、大型语言模型（LLM）对项目的理解与代码生成、项目结构可视化及自动化构建流程等场景。本规范文档定义了PIR v0.2.1版本的完整语法与语义。

2. 引言

2.1 背景与问题

在软件工程，特别是涉及复杂系统（如操作系统、大型应用框架）的开发与维护中，快速、准确地理解项目的整体架构、文件依赖和符号定义是至关重要的。传统的抽象语法树（AST）或编译器中间表示（IR）过于底层且冗余，而简单的文件列表又无法表达丰富的逻辑关系。PIR旨在填补这一空白，提供一个在信息密度和表达力之间取得平衡的“项目级思维模型”。

2.2 设计目标

PIR的设计遵循以下核心原则：

- 最小化 (Minimalism)： 严格限定所包含的信息范畴，仅保留理解项目骨架所必需的元素，避免任何形式的冗余。
- 高可读性 (Human & Machine Readable)： 格式设计兼顾人类阅读的直观性与机器解析的无歧义性。
- 易于生成 (Ease of Generation)： 能够通过编译器前端、静态分析工具或简单脚本从项目源代码中低成本生成。
- 语义明确 (Unambiguous Semantics)： 每个标签、字段和关系的含义都有清晰且唯一的定义。
- 版本稳定性 (Version Stability)： v0.2.1版本为核心冻结版本，确保基于此版本的工具链具有长期的兼容性。

2.3 范围与边界

PIR是：

- 一个描述项目逻辑结构的元数据框架。
- 一个连接项目源代码与高层分析工具（如LLM）的桥梁。

PIR不是：

- 抽象语法树 (AST)： 不解析或表示代码的具体语法结构。
- 编译器IR (如LLVM IR)： 不具备可执行性，不参与实际的编译优化或代码生成。
- 软件包规范 (如RPM SPEC)： 不描述软件打包、依赖安装或部署流程。

3. 全局结构与语法约定

PIR文档采用线性文本格式，由若干个预定义的区块（Section）顺序组成。所有区块必须按照第4节定义的顺序出现，每个区块的标签（如 
"<meta>", 
"<units>"）必须成对出现，即使区块内容为空。

3.1 文档结构顺序

一个完整的PIR文档必须遵循以下层次结构：

<pir>
<meta> ... </meta>
<units> ... </units>
<dependencies> ... </dependencies>
<symbols> ... </symbols>
<layout> ... </layout>
<code-snippets> ... </code-snippets>
</pir>

3.2 通用格式规则

- 字符编码： 建议使用UTF-8编码，以确保良好的国际字符支持。
- 路径表示： 所有路径必须使用正斜杠 (
"/") 作为分隔符，以实现跨平台兼容。绝对路径和相对路径均需遵循此规则。
- 标识符： 单元标识符（
"uX"）必须从
"u0"开始连续编号，不允许跳号。
- 空格与缩进： 建议使用空格进行缩进，保持对齐以增强可读性。虽然解析器可能忽略多余空格，但规范的格式是良好实践的一部分。

4. 区块详述

4.1 
"<meta>" - 项目元信息

本区块定义了项目的基本身份信息和生成环境。

格式：

<meta>
name: <项目名称>
root: <项目根目录的绝对路径>
profile: <构建或目标环境描述>
lang: <项目使用的主要编程语言列表，以逗号分隔>
</meta>

字段说明：

字段名 数据类型 说明与示例

"name" 字符串 项目名称，例如 
"my_os"。

"root" 字符串（路径） 项目源码树的根目录，例如 
"/home/user/projects/my_os"。

"profile" 字符串 描述构建配置或目标平台，例如 
"os-riscv", 
"c-make-arm"。

"lang" 字符串列表 项目中使用的主要编程语言，例如 
"C,ASM,LD"。

4.2 
"<units>" - 编译单元列表

本区块枚举了项目中的所有逻辑编译单元（通常是源文件）。

格式：

<units>
uX: <文件路径> type=<语言类型> role=<单元角色> module=<所属模块>
...
</units>

字段说明：

字段名 说明与示例

"uX" 单元唯一标识符，
"X"为从0开始的非负整数，例如 
"u0", 
"u1"。

"<文件路径>" 相对于
"<meta>"中
"root"的文件路径，例如 
"core/init.c"。

"type" 单元的语言类型，例如 
"C", 
"ASM", 
"LD", 
"Python"。

"role" 单元在项目中的功能角色，例如 
"entry"（入口）, 
"kernel"（内核）, 
"driver"（驱动）。

"module" 单元所属的逻辑模块，用于项目内部分组，例如 
"core", 
"mm"（内存管理）。

4.3 
"<dependencies>" - 单元间依赖关系

本区块以有向图的形式描述单元之间的依赖关系。

格式：

<dependencies>
uA-><动词>:uB
uA-><动词>:uB#<符号名>
...
</dependencies>

动词（Verb）语义：

动词 语义说明 示例

"call" 调用函数或跳转至标签。 
"u0->call:u1#page_init"

"import" 导入或引用全局变量、外部符号。 
"u0->import:u2#global_var"

"include" 包含头文件或接口定义。 
"u0->include:u3"

"use" 使用类型、宏或常量定义。 
"u1->use:u0#PAGE_SIZE"

"link" 链接时依赖，如目标文件对链接脚本的引用。 
"u0->link:u3"

语义规则：

- 依赖关系 
"uA-><verb>:uB" 表示存在文件级别的依赖。
- 依赖关系 
"uA-><verb>:uB#sym" 表示存在符号级别的精确依赖。被引用的符号 
"sym" 必须在 
"<symbols>" 区块中有定义。
- 鼓励工具生成符号级依赖关系，以提供更高精度的项目视图。

4.4 
"<symbols>" - 全局符号表

本区块集中定义项目中关键的全局符号（函数、变量、链接器标签等）。

格式：

<symbols>
<符号名>:uX <类型> [<属性名>=<属性值>, ...]
...
</symbols>

字段说明：

字段名 说明与示例

"<符号名>" 符号的名称，例如 
"start_kernel", 
"_bss_start"。

"uX" 定义该符号的单元标识符。

"<类型>" 符号的种类，例如 
"func"（函数）, 
"var"（变量）, 
"label"（汇编标签）, 
"ld"（链接器符号）。

"[属性]" （可选）符号的附加属性，以键值对形式表示，例如 
"entry=true", 
"weak=true"。

符号消歧规则：

- 允许不同单元中存在同名符号（例如，多个模块都有自己的 
"init" 函数）。
- 一个符号的全局唯一身份由 
"(符号名, 定义该符号的单元ID uX)" 二元组共同确定。所有工具和LLM在处理符号时必须遵循此规则进行消歧。

4.5 
"<layout>" - 内存布局描述

本区块专门用于描述需要链接器进行内存布局的项目（如操作系统内核、嵌入式固件）的地址空间分配。

格式：

<layout>
ENTRY=<入口符号名>
BASE=<内存基地址（十六进制）>
<段名>: <提供此段内容的单元ID列表（以空格分隔）>
...
</layout>

字段说明：

字段名 说明与示例

"ENTRY" 程序执行的入口点符号，例如 
"start_kernel"。

"BASE" 程序加载或运行的起始内存地址，例如 
"0x80000000"。

"<段名>" 标准或自定义的链接段名称，例如 
".text", 
".data", 
".bss", 
".rodata"。

"<单元列表>" 哪些单元（
"uX"）的代码或数据会被放置在此段中。

4.6 
"<code-snippets>" - 关键代码片段

本区块可选地嵌入关键代码片段，旨在为LLM或开发者提供更直观的上下文理解，其内容不参与PIR的逻辑分析。

格式：

<code-snippets>
<snippet unit="uX">
<![CDATA[
// 代码内容
]]>
</snippet>
...
</code-snippets>

说明：

- 每个 
"<snippet>" 标签通过 
"unit" 属性关联到特定的编译单元。
- 内容为纯文本，PIR规范本身不对其进行语法解析。
- 可使用注释或省略号表示非关键部分的省略。

5. 完整实例

以下是一个符合PIR v0.2.1规范的RISC-V操作系统项目示例。

<pir>
<meta>
name: my_os
root: /home/user/projects/my_os
profile: os-riscv
lang: C,ASM,LD
</meta>

<units>
u0: core/init.c type=C role=kernel module=core
u1: mm/page.c type=C role=mm module=mm
u2: boot/start.S type=ASM role=entry module=boot
u3: linker/os.ld type=LD role=linkscript module=link
</units>

<dependencies>
u2->call:u0#start_kernel
u0->call:u1#page_init
u0->include:u3
</dependencies>

<symbols>
start_kernel:u0 func entry=true
page_init:u1 func
_bss_start:u3 ld
_bss_end:u3 ld
</symbols>

<layout>
ENTRY=start_kernel
BASE=0x80000000
.text:u2 u0
.rodata:u0
.data:u0
.bss:u1 u0
</layout>

<code-snippets>
<snippet unit="u2">
<![CDATA[
    .section .text
    .globl _start
_start:
    csrr t0, mhartid
    bnez t0, park
    j start_kernel
park:
    wfi
    j park
]]>
</snippet>
<snippet unit="u0">
<![CDATA[
void start_kernel() {
    // Initialize system components...
    page_init();
    while (1) {
        // Kernel main loop...
    }
}
]]>
</snippet>
</code-snippets>
</pir>

6. 实施指南与最佳实践

6.1 文件命名与管理

- 规范文档： 建议将本规范保存为 
"SPEC.md" 或类似名称，纳入项目版本控制系统。
- PIR实例文件： 项目对应的PIR描述文件可命名为 
"<project_name>.pir" 或放在特定目录（如 
"docs/"）下。

6.2 工具链集成

- 生成工具： 可利用编译器的预处理功能（如 
"gcc -M" 生成依赖）、静态分析工具（如 
"ctags"/
"cscope" 生成符号表）或自定义脚本来生成和更新PIR文件。
- 验证工具： 建议在持续集成（CI）流程中加入PIR格式校验步骤，确保生成的PIR文件符合本规范。

6.3 与LLM的协同

- 为LLM提供PIR文件时，可优先考虑包含 
"<code-snippets>" 区块，以为其提供更丰富的上下文。
- 指导LLM在生成或修改代码时，应遵循PIR中定义的依赖关系和符号定义。

7. 版本历史

版本 日期 主要更新与说明
v0.1.0 202X-XX-XX 初始版本发布，定义基本结构。
v0.2.0 202X-XX-XX 引入 
"<symbols>" 和 
"<layout>" 区块，增强语义描述能力。
v0.2.1 2025-12-23 修复符号消歧义规则，明确路径格式，增强文档的严谨性。核心规范冻结。

8. 参考文献（规范依据）

1. RPM打包规范中对软件包元数据、依赖关系和文件列表的定义，为PIR的结构化描述提供了参考。
2. openEuler社区的软件包拆分原则和依赖关系管理理念，影响了PIR对项目模块化和依赖关系的设计思路。
3. 软件构建过程中对源码、补丁、构建步骤的规范描述，启发了PIR作为项目“蓝图”的定位。
4. 技术文档中关于格式、字段定义和清晰性的要求，被应用于本规范的撰写。
