# canon_config.py
# 依赖归一化配置文件
# 可以根据项目需求自定义标准库集合和归一化规则

# -------------------------
# Python 标准库配置
# -------------------------
PY_STDLIB_BASE = {
    "os", "sys", "argparse", "ast", "typing", "dataclasses", "abc", "re",
    "json", "math", "collections", "itertools", "functools", "pathlib",
    "datetime", "random", "hashlib", "logging", "threading", "multiprocessing",
    "io", "enum", "copy", "decimal", "fractions", "numbers", "queue",
    "secrets", "statistics", "string", "time", "uuid", "warnings", "weakref",
    "contextlib", "inspect", "pprint", "traceback", "types", "gc", "sysconfig"
}

# 可以根据项目需要添加额外的 Python 标准库
PY_STDLIB_CUSTOM = set()  # 例如: {"numpy", "pandas"}

PY_STDLIB = PY_STDLIB_BASE | PY_STDLIB_CUSTOM

# -------------------------
# C 标准库配置
# -------------------------
C_STDLIB_BASE = {
    "stdio.h", "stdlib.h", "string.h", "stdint.h", "stddef.h", "stdbool.h",
    "assert.h", "ctype.h", "errno.h", "float.h", "limits.h", "math.h",
    "time.h", "unistd.h", "fcntl.h", "signal.h", "setjmp.h", "locale.h",
    "stddef.h", "inttypes.h", "wchar.h", "wctype.h", "complex.h", "tgmath.h",
    "fenv.h", "stdalign.h", "stdnoreturn.h", "threads.h", "uchar.h"
}

# 可以根据项目需要添加额外的 C 标准库
C_STDLIB_CUSTOM = set()  # 例如: {"openssl/ssl.h", "curl/curl.h"}

C_STDLIB = C_STDLIB_BASE | C_STDLIB_CUSTOM

# -------------------------
# Rust 标准库配置
# -------------------------
RUST_STDLIB_PREFIX = "std::"

# 可以根据项目需要添加额外的 Rust 标准库前缀
RUST_STDLIB_PREFIXES = [RUST_STDLIB_PREFIX]  # 例如: ["std::", "core::"]

# -------------------------
# 自定义归一化规则
# -------------------------
# 格式: (verb_pattern, target_pattern, canonical_form)
# 其中:
#   - verb_pattern: 动词模式（如 "import", "include"）
#   - target_pattern: 目标模式（支持正则表达式）
#   - canonical_form: 归一化形式
CUSTOM_CANONICALIZATION_RULES = [
    # 示例：将所有以 "internal::" 开头的依赖归一化为 [internal]
    # ("use", r"internal::.*", "[internal]"),

    # 示例：将所有以 "company::" 开头的依赖归一化为 [company_lib]
    # ("use", r"company::.*", "[company_lib]"),
]

# -------------------------
# 归一化策略配置
# -------------------------
class CanonicalizationConfig:
    """归一化策略配置"""

    # 是否启用归一化
    enabled = True

    # 是否在归一化时保留原始依赖信息（用于调试）
    preserve_original = False

    # 是否输出归一化统计信息
    show_stats = True

    # 自定义规则优先级（数字越大优先级越高）
    custom_rule_priority = 100

    @classmethod
    def update(cls, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
