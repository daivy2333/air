**目标项目的目录结构可以是完全随意的**。

那个 `test_proj` 只是为了演示“这个工具能同时处理 C、Rust、Java、汇编”而捏造的一个混合示例。

`pirgen` 的设计核心是 **“递归扫描” (Recursive Scan)** 和 **“基于后缀的自动分发”**。它并不关心你的文件夹叫 `kernel` 还是 `my_cool_code`，也不关心文件是在根目录还是在第十层子目录下。

下面我为你详细解析这个工具的工作原理、适用范围以及详细的使用步骤。

---

### 1. 为什么它是通用的？（工作原理）

工具内部的逻辑（在 `pirgen.py` 的 `scan_project` 函数中）是这样运作的：

1. **起点**：你给它一个路径（例如 `D:/Work/MyProject`）。
2. **遍历**：它使用 `os.walk()`，这是一个地毯式搜索命令。它会钻进每一个子文件夹，不管文件夹叫什么名字（除了 `.git` 这种被我们显式过滤的）。
3. **识别**：它只看**文件后缀名**。
* 看到 `.c` -> 把它交给 `CAnalyzer`。
* 看到 `.py` -> 把它交给 `PythonAnalyzer`。
* 看到 `.rs` -> 把它交给 `RustAnalyzer`。


4. **归属**：它会自动给每个文件分配一个“模块名”。目前的逻辑很简单：**文件所在的文件夹名字就是模块名**。
* 如果你把 `main.c` 放在 `src/net/tcp/` 下，它的模块名就是 `tcp`。
* 如果你把 `main.c` 放在根目录下，它的模块名就是 `root`。



**结论**：你的项目可以是扁平的（所有文件在一层），也可以是深层嵌套的，或者是乱七八糟混在一起的，工具都能生成对应的 PIR。

---

### 2. 详细使用指南

#### 第一步：准备工具环境

你需要把刚才那几段代码保存成如下的结构（这是**工具本身**的结构，不能乱）：

```text
任意目录/pir_tool/
├── pirgen.py           <-- 主入口
├── core/
│   ├── pir_builder.py
│   └── project_model.py
└── analyzers/
    ├── __init__.py     <-- 注册表
    ├── base.py
    ├── c_analyzer.py
    ├── python_analyzer.py
    ├── java_analyzer.py
    ├── rust_analyzer.py
    └── asm_ld_analyzer.py

```

#### 第二步：准备你的目标项目

假设你有一个真实的开源项目，比如著名的 `Redis`，或者你自己的毕设项目。

位置：`/home/user/code/my_web_server`
结构可能很复杂：

```text
my_web_server/
├── README.md
├── makefile
├── backend/
│   ├── server.py
│   └── db_utils.py
└── frontend/
    └── src/
        └── App.js (目前没写JS分析器，会被忽略)

```

#### 第三步：运行命令

打开终端（Terminal 或 CMD），进入 `pir_tool` 文件夹，然后运行：

**基本用法：**

```bash
python pirgen.py /home/user/code/my_web_server

```

**推荐用法（加上项目名和配置描述）：**

```bash
python pirgen.py /home/user/code/my_web_server --name WebServerV1 --profile python-backend

```

* `path`: 你的目标项目路径（支持相对路径或绝对路径）。
* `--name`: 给生成的 PIR 文件起个名字，比如生成的会是 `WebServerV1.pir`。
* `--profile`: 这是一个标签，写在 PIR 文件头部的，用于提示下游工具（比如 AI 或 编译器）这个项目是什么类型的。

#### 第四步：查看结果

工具运行完毕后，会在当前目录下生成 `WebServerV1.pir`。打开它，你看到的将是规范化的文本：

* **Units**: 即使 `server.py` 在深层目录，这里也会列出 `backend/server.py`，并且 `module=backend`。
* **Dependencies**: 如果 `server.py` 里写了 `import db_utils`，工具会自动识别并生成 `uX->import:uY`。

---

### 3. 图解流程

这个过程就像一个“收割机”：

1. **输入**：杂乱的文件夹。
2. **处理**：机器臂（Scanner）抓取所有文件，根据颜色（后缀名）扔进不同的粉碎机（Analyzer）。
3. **输出**：整齐划一的压缩砖块（PIR 文本）。

---

### 4. 常见问题解答 (FAQ)

**Q: 我的项目里有 C++ 和 Python 混编，它能处理吗？**
**A:** **能。** 它会分别调用 `CAnalyzer` 和 `PythonAnalyzer`。生成的 PIR 里会同时包含 `type=C` 和 `type=Python` 的单元，并且如果 Python 调用了 C 的动态库（通过 import），依赖关系也会被记录（虽然目前的简单分析器可能只能记录到 `import [clib_name]` 这一层）。

**Q: 我的项目用的不是标准后缀，比如 C++ 用 `.cxx`？**
**A:** 你需要去修改 `analyzers/__init__.py`。
找到 `ANALYZER_MAP`，加一行：

```python
'.cxx': CAnalyzer(),

```

这样工具就能识别了。

**Q: 那些分析器看起来很简单（用正则匹配），能应付复杂的宏定义吗？**
**A:** **目前的实现比较基础**。
现在的版本是为了演示 PIR 规范而写的“轻量级原型”。它使用正则表达式去猜函数名和依赖。

* **优点**：不需要安装任何环境（gcc, java, rustc），直接用 python 就能跑，速度极快。
* **缺点**：如果你的代码里全是复杂的宏替换（比如 `DEFINE_FUNC(my_func)`），正则可能会漏掉。
* **进阶**：如果你需要工业级的精准度，需要修改 `c_analyzer.py`，让它去调用 `ctags` 或者 `libclang` 来获取符号，但这会增加工具的使用门槛。

### 5. 下一步建议

既然你已经有了全套代码，你可以：

1. **找一个你手头的小项目**（几十个文件左右）。
2. 运行这个工具。
3. 观察生成的 `.pir` 文件。
4. 如果你发现某些重要的依赖没被抓取出来（比如 C++ 的 `using namespace` 导致的隐式依赖），你可以尝试去修改对应语言的 `analyzer` 正则表达式。这就是维护这个工具的方式。