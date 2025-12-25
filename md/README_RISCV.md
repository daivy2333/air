# RISC-V 项目优化方案文档

本文档说明了对 PIR Reconstructor 进行 RISC-V 特定优化的实现细节和使用方法。

## 概述

本次优化针对 RISC-V 操作系统开发场景，增强了汇编处理能力，提供了专门的模板和分析工具。优化包括：

1. RISC-V 专用 Profile 配置
2. 增强的 ASM Enrichment Layer
3. RISC-V 专用模板
4. 内存布局处理
5. RISC-V 特定的依赖关系可视化

## 1. RISC-V 专用 Profile

### 位置
- `pirgen/core/profile_riscv.py`

### 功能
提供 RISC-V 特定的配置信息：

- **内存布局**：定义了 RAM 和 ROM 的标准布局
- **段定义**：包含 .text, .data, .bss, .rodata, .stack, .heap 等段
- **特殊符号**：定义了 _start, trap_vector, syscall_table 等符号
- **CSR 寄存器**：完整的 CSR 寄存器地址映射
- **异常码**：标准异常和中断原因码
- **指令集扩展**：RV32I, RV64I, RV32M 等扩展标识

### 使用示例

```python
from pirgen.core.profile_riscv import (
    RISCV_STANDARD_LAYOUT,
    RISCV_SPECIAL_SYMBOLS,
    get_csr_address,
    get_exception_code
)

# 获取标准内存布局
layout = RISCV_STANDARD_LAYOUT

# 检查是否为特殊符号
if '_start' in RISCV_SPECIAL_SYMBOLS:
    print("Found RISC-V entry point")

# 获取 CSR 寄存器地址
mstatus_addr = get_csr_address('mstatus')  # 返回 0x300

# 获取异常原因码
ecall_code = get_exception_code('ecall_s')  # 返回 0x9
```

## 2. ASM Enrichment Layer 增强

### 位置
- `pir_reconstructor/reconstruct/enrichment/asm.py`

### 新增功能

#### RISC-V 架构检测
自动检测以下 RISC-V 特征：
- ECALL 指令
- CSR 寄存器操作
- MRET/SRET 指令
- 内存屏障指令

#### 符号推断
增强的符号推断能力：
- 识别 RISC-V 特殊符号（_start, trap_vector 等）
- 提取 CSR 操作符号
- 识别中断处理函数
- 检测内存屏障操作

#### 依赖分析
RISC-V 特定的依赖分析：
- 系统调用依赖（ECALL 指令）
- 内存屏障依赖
- CSR 寄存器访问依赖

#### 入口点识别
自动识别：
- _start 符号
- 中断向量表（trap_vector, trap_entry）
- 系统调用处理函数

### 使用示例

```python
from pir_reconstructor.reconstruct.enrichment.asm import ASMEnrichmentLayer

# 创建 enrichment layer
enrichment = ASMEnrichmentLayer(pir_ast, project_root)

# 运行 enrichment
enrichment.run()

# 检查检测到的架构
if enrichment.detected_arch == 'riscv':
    print(f"Detected RISC-V extensions: {enrichment.detected_extensions}")
```

## 3. RISC-V 专用模板

### 位置
- `pir_reconstructor/templates/riscv.py`

### 提供的模板

#### 1. 标签模板
```python
riscv_label_template(sym)
```
生成 RISC-V 标签的基本框架。

#### 2. 函数模板
```python
riscv_func_template(sym)
```
生成 RISC-V 函数的标准框架，包括：
- 栈帧保存/恢复
- 返回地址处理
- 标准的函数序言和尾声

#### 3. CSR 操作模板
```python
riscv_csr_template(sym)
```
生成 CSR 寄存器操作的示例代码。

#### 4. 中断处理模板
```python
riscv_trap_template(sym)
```
生成中断/异常处理函数的框架，包括：
- 上下文保存
- 异常原因分析
- 上下文恢复

#### 5. 内存屏障模板
```python
riscv_memory_barrier_template(sym)
```
生成内存屏障指令的使用示例。

### 使用示例

```python
from pir_reconstructor.templates import riscv

# 使用函数模板生成代码
code = riscv.riscv_func_template(symbol)

# 使用中断处理模板
trap_code = riscv.riscv_trap_handler(symbol)
```

## 4. 内存布局处理

### 位置
- `pir_reconstructor/reconstruct/layout.py`

### 功能

#### RISCVLayoutGenerator
主要的链接器脚本生成器，提供：

1. **内存区域定义**
   - RAM 区域
   - ROM 区域
   - 自定义区域

2. **段布局**
   - .text（代码段）
   - .rodata（只读数据）
   - .data（已初始化数据）
   - .bss（未初始化数据）
   - .stack（栈）
   - .heap（堆）

3. **特殊符号**
   - _stack_start/_stack_end
   - _heap_start/_heap_end
   - 入口点定义

### 使用示例

```python
from pir_reconstructor.reconstruct.layout import RISCVLayoutGenerator

# 创建生成器
generator = RISCVLayoutGenerator(pir_ast, project_root)

# 生成链接器脚本
linker_script = generator.generate()

# 保存到文件
with open('linker.ld', 'w') as f:
    f.write(linker_script)
```

### 提取内存布局信息

```python
from pir_reconstructor.reconstruct.layout import extract_memory_layout

# 从 PIR 提取布局信息
layout = extract_memory_layout(pir_ast)

# 访问布局信息
print(f"Entry point: {layout['entry_point']}")
print(f"Sections: {layout['sections']}")
```

## 5. RISC-V 特定的依赖关系可视化

### 位置
- `pir_reconstructor/reconstruct/relations.py`

### 新增图表

#### 1. 内存布局图
- 文件：`diagrams/memory_layout.dot`
- 内容：
  - 内存区域（RAM/ROM）
  - 各段的布局
  - 入口点位置

#### 2. 系统调用流程图
- 文件：`diagrams/syscall_flow.dot`
- 内容：
  - 用户应用
  - ECALL 指令
  - Trap 处理器
  - 系统调用分发器
  - 系统调用表
  - 系统调用实现
  - 返回流程

### 自动检测

RelationLayer 会自动检测 RISC-V 项目，并在检测到时生成额外的图表：

```python
from pir_reconstructor.reconstruct.relations import RelationLayer

# 创建关系层
relation_layer = RelationLayer(pir_ast, output_dir)

# 运行（会自动检测 RISC-V 项目）
relation_layer.run()

# 如果是 RISC-V 项目，会额外生成：
# - diagrams/memory_layout.dot
# - diagrams/syscall_flow.dot
```

## 集成到 Pipeline

所有这些优化都自动集成到重建流程中：

```python
from pir_reconstructor.reconstruct.pipeline import ReconstructionPipeline

# 创建并运行 pipeline
pipeline = ReconstructionPipeline(pir_ast, project_root, output_dir)
pipeline.run()

# 对于 RISC-V 项目，会自动：
# 1. 使用 RISC-V profile
# 2. 应用 RISC-V enrichment
# 3. 生成 RISC-V 特定的图表
# 4. 使用 RISC-V 模板
```

## 最佳实践

1. **符号命名**
   - 使用 RISC-V 标准符号名（_start, trap_vector 等）
   - 遵循 RISC-V CSR 寄存器命名规范

2. **内存布局**
   - 使用标准内存布局（RISCV_STANDARD_LAYOUT）
   - 根据需要调整区域大小和属性

3. **异常处理**
   - 为每个异常类型提供处理函数
   - 使用标准异常原因码

4. **系统调用**
   - 使用标准的系统调用号
   - 实现完整的系统调用表

5. **文档生成**
   - 利用自动生成的图表理解系统结构
   - 检查内存布局图确保正确性
   - 使用系统调用流程图优化调用路径

## 故障排除

### 问题：未检测到 RISC-V 项目

**解决方案**：
1. 确保项目包含 RISC-V 特定符号（_start, trap_vector）
2. 检查汇编文件是否包含 RISC-V 特定指令（ECALL, MRET, SRET）
3. 验证链接器脚本（.ld）是否正确配置

### 问题：生成的链接器脚本不正确

**解决方案**：
1. 检查 PIR 中的 layout_lines 是否包含正确的信息
2. 验证内存区域定义是否完整
3. 确认段定义符合项目需求

### 问题：系统调用流程图未生成

**解决方案**：
1. 确保汇编文件中包含 ECALL 指令
2. 检查 enrichment layer 是否正确运行
3. 验证依赖关系是否正确识别

## 扩展指南

### 添加新的 CSR 寄存器

在 `profile_riscv.py` 中添加：

```python
RISCV_CSR_REGISTERS = {
    # 现有寄存器...
    'my_custom_csr': 0xABC,  # 添加自定义 CSR
}
```

### 添加新的异常类型

```python
RISCV_EXCEPTION_CODES = {
    # 现有异常...
    'my_custom_exception': 0x20,  # 添加自定义异常码
}
```

### 自定义内存布局

```python
from pir_reconstructor.reconstruct.layout import RISCVLayoutGenerator, MemoryRegion, Section

# 创建自定义布局
generator = RISCVLayoutGenerator(pir_ast, project_root)

# 添加自定义区域
generator.regions['custom'] = MemoryRegion(
    name='custom',
    origin='0x90000000',
    length='64M',
    attributes='wxa!ri'
)

# 添加自定义段
generator.sections.append(Section(
    name='.custom',
    region='custom',
    align=4,
    flags='wa'
))
```

## 参考资料

- [RISC-V 规范](https://riscv.org/specifications/)
- [RISC-V 特权架构](https://github.com/riscv/riscv-isa-manual)
- [RISC-V 系统调用规范](https://github.com/riscv/riscv-pk)
