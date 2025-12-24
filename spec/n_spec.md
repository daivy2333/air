PIR逆向工程规范 v1

1. 设计原则

1.1 冻结正向原则

• 不假设PIR提供未声明信息

• 不要求修改PIR v1

• 所有缺失语义通过降级规则处理

1.2 能力边界

逆向工程只保证结构可逆：
• ✅ 文件结构可逆

• ✅ 符号声明可逆  

• ✅ 依赖关系可逆

• ❌ 行为/逻辑不可逆

2. 分层模型

逆向工程严格分为五层，任何一层失败则整体失败：

结构层 (units) → 接口层 (symbols) → 关系层 (dependencies) → 文档层 → 审计层


3. 结构层规范

3.1 文件生成规则

1. 每个unit对应一个物理文件
2. unit.path逐字使用，不重命名
3. 输出路径：<output>/src/<unit.path>

3.2 禁止行为

• ❌ 基于module创建目录

• ❌ 自动归类/扁平化

• ❌ 路径重写

3.3 文件类型降级

类型 处理方式

源码文件 (PY/C/Java/RS) 生成语言骨架

头文件 生成空头+防卫宏

ASM/LD 空文件+注释

未知类型 空文件+警告

4. 接口层规范

4.1 符号作用域降级

• 所有func → 文件级符号

• 所有class/struct → 顶层定义

• 不生成方法、成员、继承关系

4.2 属性确定性处理

1. 属性按字典序排序
2. 不解释，仅展示
3. 布尔值序列化为固定字符串

Python示例模板：
def main():  # PIR_ID: main:u0
    """
    来源: u0, role: lib, module: pirgen
    属性: entry=true
    """
    # AI_TODO: 实现
    pass


5. 关系层规范

5.1 依赖池解析

pool表达式 语义

ref:uX 单元依赖

sym:uX#S 符号依赖

ext:[stdlib:py] 外部依赖

import:[mod] 模块依赖

5.2 依赖图数据模型

class DependencyEdge:
    src_unit: str
    dst_unit: Optional[str]
    dst_symbol: Optional[str]
    dep_kind: str        # import/call/include
    target_kind: str     # unit/symbol/external


5.3 可视化规范

必须包含图例，支持：
• Mermaid

• Graphviz DOT

• PlantUML

6. 文档层规范

6.1 profiles使用规则

• 不影响代码生成

• 仅用于架构文档和实现提示

示例输出：

Active Profile: python-framework
置信度: 0.8
Signals: layered-architecture, multi-module


6.2 layout处理

• 存在<layout> → 生成文档

• 不存在 → 不生成占位

• 不影响文件结构

7. 输出结构


<project>-reconstructed/
├── src/                    # 结构层输出
├── documentation/          # 文档层输出
├── diagrams/               # 关系层输出
├── .pir-metadata/          # 审计层输出
└── README.md


8. 确定性要求

8.1 排序规范

• Units: 按u0, u1, u2…顺序

• Symbols: 按PIR声明顺序

• Dependencies: 按d0, d1, d2…顺序

8.2 固定模板

所有语言模板必须硬编码，不得运行时生成：
• 注释格式固定

• 缩进空格数固定

• 时间戳固定（1970-01-01）

8.3 哈希验证

每次生成必须计算输出哈希，相同输入必须产生相同哈希。

9. 优先级规则

9.1 代码片段优先级


<code-snippets> > 骨架生成 > 通用模板


冲突处理：snippet完全替换对应符号骨架

9.2 分层优先级

1. 结构层
2. 接口层
3. 关系层
4. 文档层
5. 审计层

前一层失败必须终止后续层

10. 错误处理

10.1 分层错误

class ReconstructionError(Exception):
    level: str  # 'structure'|'interface'|'relation'
    message: str
    partial_output: Any


10.2 处理策略

错误类型 处理方式 是否终止

路径冲突 重命名+警告 否

无效文件类型 生成空文件+警告 否

磁盘空间不足 抛出StructureError 是

验证失败 抛出当前层级Error 是

11. 验证要求

11.1 必须验证

1. 文件数量一致性
2. 路径完全匹配
3. 符号覆盖率100%
4. 依赖完整性
5. snippet覆盖验证
6. 输出哈希一致性

11.2 测试要求

必须包含：
• 确定性测试

• 分层顺序测试

• snippet优先级测试

• 错误处理测试

12. 禁止行为

逆向工程明确禁止：

1. 推断缺失信息
   • 禁止猜测未声明符号

   • 禁止推断函数参数

   • 禁止推断数据类型

2. 修改结构
   • 禁止重命名文件

   • 禁止移动文件位置

   • 禁止合并/拆分模块

3. 补全依赖
   • 禁止添加未声明依赖

   • 禁止推断传递依赖

   • 禁止修正循环依赖

4. 非确定性行为
   • 禁止使用随机数

   • 禁止依赖时间戳

   • 禁止依赖环境变量

   • 禁止依赖遍历顺序

5. 语义推断
   • 禁止推断算法逻辑

   • 禁止推断性能优化

   • 禁止推断错误处理

13. 向后兼容性

PIR逆向工程v1承诺：

1. 格式稳定性：v1.1输出格式稳定
2. 语义稳定性：不改变生成文件语义
3. 确定性保证：相同输入永远产生相同输出
4. 扩展不破坏：新功能不破坏现有生成确定性

版本: v1
状态: 正式规范  
生效日期: 2025-12-24  
变更说明: 新增确定性要求、分层顺序约束、snippet优先级规则  
维护者: daivy 
许可证: MIT