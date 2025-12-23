# PIR Generator 更新日志

## [0.3.0] - 2025-12-23

### 新增功能

#### 依赖语义归一化（Dependency Canonicalization）

- 新增 `core/dep_canon.py` 模块，实现依赖语义归一化功能
- 将标准库依赖归一化为语义形式：
  - Python: `[os]`, `[sys]`, `[re]` 等标准库 → `[stdlib:py]`
  - C: `[stdio.h]`, `[stdlib.h]` 等标准头文件 → `[stdlib:c]`
  - Rust: `[std::xxx]` → `[stdlib:rust]`
- 在 PIR 生成流程中新增 `canonicalize_dependencies` 阶段
- 完整的 pipeline：
  ```
  scan_project
  → resolve_dependencies
  → canonicalize_dependencies  ← 新增
  → finalize_dependencies
  → emit PIR
  ```

### 改进

#### 标准库支持扩展

- Python 标准库集合扩展至 40+ 个常用模块
- C 标准库集合扩展至 30+ 个常用头文件
- Rust 标准库通过前缀匹配支持所有 `std::` 开头的路径

### 文档

- 新增 `README_CANON.md` 详细说明依赖归一化功能
- 更新主 `README` 文件，添加 PIR 生成流程说明
- 新增 `example_canonicalization.py` 示例代码，展示归一化效果

### 技术细节

- 归一化过程不影响项目内部依赖的解析
- 只有标准库依赖会被归一化，外部依赖保持原样
- 归一化在依赖解析之后进行，确保符号引用的正确性
- 完全兼容 PIR v0.3 规范，无需修改 IR 核心结构

### 效果

- Token 数量显著减少（多个标准库依赖合并为一个）
- 语义表达能力增强（通过 `[stdlib:py]` 等语义标识）
- PIR 文件更加简洁，便于 LLM 理解和分析
