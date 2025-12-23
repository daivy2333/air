PIR — Project Intermediate Representation  
Version: v0.2  
Status: Frozen (Stable Core)  

🎯 目标  
PIR 是一种面向项目级别的中间表示，以最小 token 成本表达软件项目的结构与语义骨架，用于：  
- 静态分析｜架构理解｜LLM 项目推理｜跨语言统一表示  
不是 AST、LLVM IR 或可执行格式。

🧱 全局结构（固定顺序，区块可空）

<PIR>
<META>...</META>
<UNITS>...</UNITS>
<GRAPH>...</GRAPH>
<SYMBOLS>...</SYMBOLS>
<STRUCTURE>...</STRUCTURE>  # 可选，原 LAYOUT 泛化
<CODE>...</CODE>
</PIR>


1. ：项目元信息
name: my_os
root: /path/to/project
profile: c-make-riscv          # ← 决定解析规则
lang: C,ASM
kind: os-kernel                # ← 新增！类型：os-kernel | web-app | lib | cli-tool | data-pipeline ...

2. ：翻译单元（文件级）
u0:src/main.c type=C role=entry module=init
u1:models/user.py type=Python role=model module=auth

- uX：全局唯一 ID  
- type：语法类型（C/Python/Rust/XML...）  
- role：功能角色（entry, lib, test, config, model...）  
- module：逻辑模块（由 profile 定义，替代原 arch）

3. ：依赖关系（文件级）
u0->include:stdio.h            # C 头文件
u1->import:django.contrib.auth # Python 模块
u2->call:u1                    # 跨文件函数调用
u3->build-depends:u0           # 构建依赖

- 左侧必须是 uX  
- 动词标准化：include｜import｜call｜build-depends｜data-flow  
- 不保证 完备性或链接顺序

4. ：最小符号表
main:u0 func entry=true
User:u1 class
LOG_LEVEL:u3 const config=true

- 格式：name:uX role [attr=value]*  
- role：func｜class｜struct｜const｜endpoint｜route...  
- 不区分 可见性，不保证 完全覆盖

5. （可选）：项目结构语义
- OS 项目：内存布局（.text @0x8000, .data...）  
- Web 项目：路由映射（/api/users → u1）  
- ML 项目：数据流（load → preprocess → train）  
- 内容由 kind 决定，PIR 不强制格式

6. ：最小代码证据

// ENTRY POINT
int main() { return 0; }

- 非完整源码，仅保留关键上下文（如入口、接口签名）  
- 可安全截断，用于模式识别

🔌 扩展规则
- ✅ 允许新增区块（如 ）  
- ❌ 禁止修改已有区块语义  
- 新语言通过 profile + 新 parser 接入

📜 设计原则
PIR ≠ AST  
PIR ≠ IR  
PIR = “项目级可编译思维模型”  

这份规范既保留了你在 RISC-V OS 场景下的精确需求，又通过 kind/role/GRAPH 动词 等机制实现了对 Python、Java、Rust 等项目的优雅泛化，同时对 LLM、人类和工具链都高度友好