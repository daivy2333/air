PIR — Project Intermediate Representation  
Version: v0.2.1  
Status: Frozen (Stable Core)  

PIR 是一种面向项目级别的中间表示，用于在不完整编译、不执行、不链接的前提下，以最小 token 成本表达一个软件项目的结构与语义骨架。

1. 设计目标（Design Goals）

PIR 适用于：
- 静态架构分析  
- LLM 项目理解与推理  
- 跨语言统一表示  
- 编译器前端输出抽象  
- 构建/依赖可视化  

PIR 不是：
- 抽象语法树（AST）  
- 编译器 IR（如 LLVM IR）  
- 可执行或可链接格式  

核心理念：PIR = “项目级可编译思维模型”

2. 全局结构（Top-Level Layout）

PIR 使用线性文本格式，区块顺序固定，所有区块可为空：

<PIR>
<META>...</META>
<UNITS>...</UNITS>
<GRAPH>...</GRAPH>
<SYMBOLS>...</SYMBOLS>
<STRUCTURE>...</STRUCTURE>  <!-- 可选 -->
<CODE>...</CODE>
</PIR>


3. ：项目元信息

描述项目上下文与生成环境。

格式

name: my_project
root: /absolute/path/to/project
profile: c-make-riscv
lang: C,ASM
kind: os-kernel
version: 1.0.0             
pir_version: 0.2.1         
timestamp: 2025-12-23T11:20:00+08:00  

字段说明
字段   必需   含义
name   ✓   项目名称
root   ✓   分析时的项目根路径（绝对）
profile   ✓   解析配置标识（如 python-django, rust-cargo-cli）
lang   ✓   涉及的语言列表（逗号分隔）
kind   ✓   项目类型（见下表）
version   ✗   项目自身的语义版本（如 Git tag）
pir_version   ✗   本 PIR 文档所遵循的规范版本
timestamp   ✗   生成时间（ISO 8601）

推荐 kind 值
- os-kernel, firmware, embedded
- web-app, microservice, api-server
- lib, sdk, framework
- cli-tool, script
- data-pipeline, ml-training

4. ：翻译单元（文件级）

表示最小编译/解析单元（通常为文件）。

格式

u0:src/main.c type=C role=entry module=core
u1:models/user.py type=Python role=model module=auth
u2:Cargo.toml type=TOML role=build-config module=root

字段说明
字段   含义
uX   全局唯一单元 ID（X 为非负整数）
path   相对于 root 的路径
type   文件语法类型（C/Python/Rust/XML/TOML/YAML 等）
role   功能角色（见下表）
module   逻辑模块名（由 profile 定义，用于分组）

推荐 role 值
- entry, lib, test, config, build-script
- model, view, controller, route, middleware（Web）
- resource, doc, fixture, migration

保证：uX 在单个 PIR 中唯一  
不保证：module 语义跨项目一致

5. ：依赖关系图（文件级）

表达单元间的依赖，支持可选符号精度。

格式

u0->include:stdio.h
u1->import:django.contrib.auth
u2->call:u1                
u2->call:u1#kalloc         
u3->build-depends:u0
u4->data-flow:logs.csv

语义规则
- 左侧必须是  中定义的 uX
- 右侧格式：[target] 或 [target]#[symbol]
- 标准化依赖动词：
  - include：C/C++ 头文件包含
  - import：模块导入（Python/Java/Rust）
  - call：函数/方法调用（静态可推断）
  - build-depends：构建时依赖
  - data-flow：数据输入/输出依赖

符号链接约束
- 若使用 uA->verb:uB#sym，则 sym 应当在  中有定义（如 sym:uB func）
- 若未使用 #sym，则仅表示“存在某种依赖”，不要求符号显式声明

️ 不表示 链接顺序、运行时依赖或动态加载

️ 6. ：最小符号表

提供支持语义推理的符号证据。

格式

main:u0 func entry=true
User:u1 class
kalloc:u2 func
LOG_LEVEL:u3 const config=true
_start:u4 ld

字段说明
- 格式：name:uX role [attr=value]*
- name：符号标识符
- uX：定义该符号的单元
- role：符号类型（见下表）
- attr=value：可选属性（空格分隔）

推荐 role 值
- func, class, struct, trait, interface, enum
- var, const, macro, type
- endpoint, route, task, ld（链接器符号）

常见属性
- entry=true：程序入口点
- config=true：配置项
- http-method=GET/POST
- ml-task=train|eval

不区分 可见性（public/private）  
不保证 符号表完整覆盖

️ 7. ：项目结构语义（可选）

表达项目高层组织结构，格式由 kind 决定。

推荐子格式（按 kind）
kind   推荐格式示例
os-kernel    .text: .text* @0x80000000.data: .data.bss: .bss 
web-app    /api/users → u1 method=GET/login → u2 method=POST 
data-pipeline    load: u0 input=raw.csvtrain: u1 output=model.pkl 
lib / cli   可留空，或列出主模块：main_module: u0

推荐（SHOULD） 使用上述格式以提升工具兼容性  
不要求（MUST NOT） 强制解析器支持所有格式

8. ：最小代码证据

提供不可压缩的关键代码片段，用于上下文理解。

格式

// ENTRY POINT
int main() { return kernel_init(); }

class User(models.Model):
    name = models.CharField(max_length=100)

语义
- 非完整源码，仅保留接口、入口、关键逻辑
- 可安全截断（如省略函数体）
- 鼓励使用注释标记关键位置（如 // ENTRY POINT）

9. 扩展规则（Extensibility）

-  允许新增区块（如 , ）
-  禁止修改已有区块的字段语义
- 新语言/框架应通过新 profile + 新 parser 接入
- 自定义 kind 可自由定义  格式

10. 版本与兼容性

- v0.2.x：向后兼容，仅增补可选字段或语义澄清
- 结构性变更（如新增必需字段）须升级至 v0.3
- 工具应优先检查  中的 pir_version

PIR ≠ AST  
PIR ≠ IR  
PIR = 项目级可编译思维模型

这份规范已准备好用于工程实现。你可以基于它开发：
- 多语言 PIR 生成器（按 profile 路由）
- PIR → LLM Prompt 适配器
- PIR → 可视化依赖图工具
