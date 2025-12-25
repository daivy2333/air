# core/dep_canon.py
"""
依赖语义归一化（Dependency Canonicalization）

将各种形式的依赖目标（如 [os], [sys], [stdio.h] 等）
归一化为语义级别的标准形式（如 [stdlib:py], [stdlib:c] 等）
"""

# -------------------------
# 语义依赖表
# -------------------------
PY_STDLIB = {
    "os", "sys", "argparse", "ast", "typing", "dataclasses", "abc", "re",
    "json", "math", "collections", "itertools", "functools", "pathlib",
    "datetime", "random", "hashlib", "logging", "threading", "multiprocessing",
    "io", "enum", "copy", "decimal", "fractions", "numbers", "queue",
    "secrets", "statistics", "string", "time", "uuid", "warnings", "weakref",
    "contextlib", "inspect", "pprint", "traceback", "types", "gc", "sysconfig"
}

C_STDLIB = {
    "stdio.h", "stdlib.h", "string.h", "stdint.h", "stddef.h", "stdbool.h",
    "assert.h", "ctype.h", "errno.h", "float.h", "limits.h", "math.h",
    "time.h", "unistd.h", "fcntl.h", "signal.h", "setjmp.h", "locale.h",
    "stddef.h", "inttypes.h", "wchar.h", "wctype.h", "complex.h", "tgmath.h",
    "fenv.h", "stdalign.h", "stdnoreturn.h", "threads.h", "uchar.h"
}

RUST_STDLIB_PREFIX = "std::"

# -------------------------
# Canonicalization 核心
# -------------------------
def canonicalize_target(verb: str, target: str) -> str:
    """
    将依赖目标归一化为语义形式

    Args:
        verb: 依赖动词（import/include/use/link等）
        target: 原始目标（如 [os], [stdio.h] 等）

    Returns:
        归一化后的目标字符串
    """
    if not target.startswith("["):
        return target

    raw = target[1:-1]

    # Python stdlib
    if raw in PY_STDLIB:
        return "[stdlib:py]"

    # C stdlib
    if raw in C_STDLIB:
        return "[stdlib:c]"

    # Rust std
    if raw.startswith(RUST_STDLIB_PREFIX):
        return "[stdlib:rust]"

    # 其他情况保持不变
    return target


def canonicalize_dependencies(model):
    """
    对整个 ProjectModel 应用依赖归一化

    Args:
        model: ProjectModel 实例
    """
    if model.deps_finalized:
        raise RuntimeError("Cannot canonicalize after finalize_dependencies")

    new_unit_keys = {}
    new_all = set()

    for uid, keys in model._unit_dep_keys.items():
        new_keys_set = set()
        for k in keys:
            verb, target = k.split(":", 1)
            new_target = canonicalize_target(verb, target)
            new_k = f"{verb}:{new_target}"
            new_keys_set.add(new_k)
            new_all.add(new_k)
        new_unit_keys[uid] = list(new_keys_set)

    model._unit_dep_keys = new_unit_keys
    model._all_dep_keys = new_all
