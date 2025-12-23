PIR (Project Intermediate Representation) 规范核心 (v0.3草案)

版本: v0.3 (草案)
状态: 核心概念稳定
日期: 2025-12-23

1. 设计目标

PIR 旨在为多语言软件项目提供一个极简的、机器可读的中间表示，专注于描述项目的核心结构、模块依赖及关键语义。它服务于静态分析、LLM项目理解、架构可视化等场景。PIR 不是抽象语法树（AST）或可执行的编译器IR。

2. 文档全局结构

PIR 文档采用线性文本格式，区块顺序固定。
<pir>
<meta> ... </meta>
<units> ... </units>
<dependency-pool> ... </dependency-pool> <!-- 新增核心区块 -->
<dependencies> ... </dependencies>
<symbols> ... </symbols>
<layout> ... </layout>          <!-- 可选 -->
</pir>


3. 区块定义

3.1 <meta> - 项目元信息

定义项目的基本身份和生成环境。
<meta>
name: <项目名称>
root: <项目根目录的绝对路径>
profile: <构建或目标环境描述>  <!-- 如 `os-riscv`, `python-django` -->
lang: <项目使用的主要编程语言列表，以逗号分隔>
</meta>


3.2 <units> - 编译单元列表

枚举项目中的逻辑编译单元（通常是源文件）。
<units>
uX: <文件路径> type=<语言类型> role=<单元角色> module=<所属模块>
</units>

• uX: 单元唯一标识符（u0, u1...）。

• type: 单元的语言类型（如 C, Python, Rust, TOML）。

• role: 功能角色（如 entry, lib, config, model）。

• module: 逻辑模块名（用于项目内部分组）。

3.3 <dependency-pool> - 依赖关系池 (新增)

集中定义项目中所有可能的依赖关系实例。此设计旨在消除重复描述，实现依赖关系的重用。
<dependency-pool>
dX: <动词>:<目标>
</dependency-pool>

• dX: 依赖关系唯一标识符（d0, d1...）。

• <动词>:<目标>: 定义依赖的语义，与之前规范一致。

    ◦ 动词：call, import, include, use, link。

    ◦ 目标：uX（内部单元）, [外部标识符]（外部依赖）, uX#<符号名>（符号级依赖）。

3.4 <dependencies> - 单元依赖映射

描述编译单元与依赖关系池之间的引用，而非直接定义依赖。
<dependencies>
uA->refs:[dX dY ...]
</dependencies>

• uA->refs:[dX dY ...]: 表示单元 uA 引用了依赖池中标识符为 dX, dY ... 的依赖关系。

3.5 <symbols> - 全局符号表

集中定义项目中关键的全局符号。
<symbols>
<符号名>:uX <类型> [<属性名>=<属性值>, ...]
</symbols>

• 类型: func, class, var, const, route 等。

• 属性: （可选）如 entry=true, http-method=GET。

• 符号消歧: 符号的全局唯一性由 (符号名, 定义该符号的单元ID uX) 二元组确定。

3.6 <layout> - 项目结构语义（可选）

描述项目高层组织结构，其格式由项目类型决定。
<layout>
<!-- 格式灵活，由项目类型决定 -->
<!-- 示例 (OS内核): -->
ENTRY=start_kernel
BASE=0x80000000
.text: u2 u0
.data: u0 u1
</layout>


4. 核心优势与多语言适用性

• 依赖关系复用：通过 <dependency-pool>，相同的依赖（如一个被多处引用的公共头文件 [stdio.h]）只需定义一次（dX），即可被多个单元（uA, uB...）通过 refs 引用，极大减少了描述冗余。这对于大型项目尤其有利。

• 语义精确与清晰：<dependencies> 区块现在只负责映射，职责单一，结构更清晰。

• 多语言支持：动词（import, include）和目标类型（外部标识符）的设计，使其能够自然描述不同语言的依赖模式，例如：

    ◦ C/C++: d0: include:[stdio.h]

    ◦ Python: d1: import:[django.contrib.auth]

    ◦ Rust: d2: use:[std::collections::HashMap]

5. 实例（基于您提供的实例）

此实例展示了新规范的应用。
<pir>
<meta>
name: my_os
root: /home/user/projects/my_os
profile: os-riscv
lang: C,ASM,LD
</meta>
<units>
u0: core/init.c type=C role=entry module=core
u1: mm/page.c type=C role=mm module=mm
u2: boot/start.S type=ASM role=boot module=boot
</units>
<dependency-pool>
d0: call:u0#start_kernel
d1: call:u1#page_init
d2: include:[stdio.h]
</dependency-pool>
<dependencies>
u2->refs:[d0]  <!-- 启动代码调用内核入口 -->
u0->refs:[d1 d2] <!-- 内核入口调用页初始化函数，并包含标准IO -->
</dependencies>
<symbols>
start_kernel:u0 func entry=true
page_init:u1 func
</symbols>
<layout>
ENTRY=start_kernel
BASE=0x80000000
.text: u2 u0
.data: u0 u1
</layout>
</pir>


6. 版本说明

• v0.3 (草案)：引入 <dependency-pool> 概念，实现依赖关系的集中定义与复用，优化了 <dependencies> 区块的语义。此设计显著提升了PIR在描述复杂、多语言项目时的简洁性和可维护性。

这份更新后的规范通过引入依赖关系池的概念，使PIR在保持核心目标不变的同时，结构更加优雅和强大，非常适合于您开发能覆盖多种语言的工具。