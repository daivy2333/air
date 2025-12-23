PIR (Project Intermediate Representation) 规范核心

版本: v0.2.1 (语义精确定义修订)

状态: 核心规范冻结 (Stable Core)

日期: 2025-12-23

1. 设计目标

PIR 旨在为软件项目提供一个轻量级、跨语言的中间表示，专注于描述项目的核心结构、模块依赖及关键语义。它服务于静态分析、LLM项目理解、架构可视化等场景。PIR 不是抽象语法树（AST）或可执行的编译器IR。

2. 文档全局结构

PIR 文档采用线性文本格式，区块顺序固定。

<pir>
<meta> ... </meta>
<units> ... </units>
<dependencies> ... </dependencies>
<symbols> ... </symbols>
<layout> ... </layout>          <!-- 可选 -->
<code-snippets> ... </code-snippets> <!-- 可选 -->
</pir>

3. 区块定义

3.1 
"<meta>" - 项目元信息

定义项目的基本身份和生成环境。

<meta>
name: <项目名称>
root: <项目根目录的绝对路径>
profile: <构建或目标环境描述>  <!-- 如 `c-make-riscv`, `rust-cargo` -->
lang: <项目使用的主要编程语言列表，以逗号分隔> <!-- 如 `C,ASM`, `Python,Rust` -->
</meta>

3.2 
"<units>" - 编译单元列表

枚举项目中的逻辑编译单元（通常是源文件）。

<units>
uX: <文件路径> type=<语言类型> role=<单元角色> module=<所属模块>
</units>

- 
"uX": 单元唯一标识符（
"u0", 
"u1"...）。
- 
"type": 单元的语言类型（如 
"C", 
"Python", 
"Rust"）。
- 
"role": 功能角色（如 
"entry", 
"lib", 
"driver", 
"config"）。
- 
"module": 逻辑模块名（用于项目内部分组）。

3.3 
"<dependencies>" - 依赖关系图

描述单元间及单元与外部实体间的依赖关系。

<dependencies>
uA-><动词>:<目标>
</dependencies>

- 目标类型：
   - 
"uX": 引用本项目内定义的单元。
   - 
"[外部标识符]": 引用系统库或外部包（如 
"[stdio.h]"）。
   - 
"uX#<符号名>": 引用本项目内特定单元的符号（提供符号级精度）。
- 动词语义:
   - 
"call": 调用函数或跳转至标签。
   - 
"import": 导入或引用全局变量、外部符号。
   - 
"include": 包含头文件或接口定义。
   - 
"use": 使用类型、宏或常量定义。
   - 
"link": 链接时依赖。

3.4 
"<symbols>" - 全局符号表

集中定义项目中关键的全局符号。

<symbols>
<符号名>:uX <类型> [<属性名>=<属性值>, ...]
</symbols>

- 类型: 
"func", 
"var", 
"class", 
"struct", 
"ld"（链接器符号）等。
- 属性: （可选）如 
"entry=true", 
"config=true"。
- 符号消歧: 符号的全局唯一性由 
"(符号名, 定义该符号的单元ID uX)" 二元组确定。

3.5 
"<layout>" - 项目结构语义（可选）

描述项目高层组织结构，其格式由项目类型（可在 
"<meta>" 的 
"profile" 或项目特性中隐含）决定。例如，对于操作系统内核，可描述内存布局；对于Web应用，可描述路由映射。

<layout>
<!-- 格式灵活，由项目类型决定 -->
<!-- 示例 (OS内核): -->
ENTRY=start_kernel
BASE=0x80000000
.text: u0 u1
.data: u2
</layout>

3.6 
"<code-snippets>" - 关键代码片段（可选）

嵌入不可压缩的关键代码片段，为上下文理解提供锚点。内容不参与PIR的逻辑分析。

<code-snippets>
<snippet unit="uX">
<![CDATA[
// 代码内容，如入口函数或关键接口
]]>
</snippet>
</code-snippets>

4. 扩展性与兼容性

- 扩展规则: 允许新增区块，禁止修改已有区块的字段语义。
- 多语言支持: 新语言或框架通过定义新的 
"profile" 和对应的解析器接入。
- 版本管理: v0.2.x 系列保持向后兼容，结构性变更将升级主版本号。

5. 实例（RISC-V OS 精简示例）

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
<dependencies>
u2->call:u0#start_kernel
u0->call:u1#page_init
u0->include:[stdio.h]
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

此精简规范保留了PIR作为多语言项目描述工具的核心要素，便于您进行工具开发。其设计借鉴了现代编译器中间表示分层和多语言项目中问表示的统一抽象思想，确保了架构的清晰性和扩展性。