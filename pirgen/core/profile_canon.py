# core/profile_canon.py
"""
Profile Canonicalization (Profile-Aware Semantic IR)

Language-owned, dominance-aware semantic profile inference.
"""

from typing import Dict, List, Set, Optional
from collections import Counter

# ============================================================
# Language Constants
# ============================================================

LANG_PY = "PY"
LANG_RS = "RS"
LANG_C = "C"
LANG_CPP = "CPP"
LANG_JAVA = "JAVA"
LANG_RUST = "Rust"

# ============================================================
# Library Signals
# ============================================================

# ML Python Profile Rules
ML_PYTHON_LIBS = {
    "numpy", "torch", "tensorflow", "keras", "scikit-learn", "pandas",
    "matplotlib", "seaborn", "scipy", "jax", "flax", "pytorch_lightning",
    "transformers", "datasets", "accelerate", "optimum", "onnx", "xgboost"
}

# Python Tool Profile Rules
PYTHON_TOOL_LIBS = {
    "stdlib",  # Match normalized stdlib:py, stdlib:c, etc.
    "argparse", "pathlib", "dataclasses", "typing", "collections",
    "os", "sys", "json", "re", "logging"
}

# -------------------------
# C / System Profile Rules
# -------------------------
C_STDLIB_TARGETS = {
    "stdlib",   # stdlib:c
    "libc",
}

EMBEDDED_C_LIBS = {
    "newlib",
    "musl",
    "uclibc",
    "freertos",
    "zephyr",
}

KERNEL_C_SIGNALS = {
    "arch",
    "mm",
    "sched",
    "irq",
}

# C++ 竞赛编程特征
CPP_COMPETITIVE_PATTERNS = {
    "icpc",
    "acm",
    "codeforces",
    "atcoder",
    "leetcode",
    "hackerrank",
}

CPP_STD_HEADERS = {
    "iostream",
    "vector",
    "algorithm",
    "string",
    "map",
    "set",
    "queue",
    "stack",
}

# -------------------------
# Rust Profile Rules
# -------------------------
RUST_STDLIB_TARGETS = {
    "std",
    "core",
    "alloc",
}

RUST_EMBEDDED_LIBS = {
    "riscv-rt",
    "embedded-hal",
    "cortex-m-rt",
    "no_std",
}

RUST_WEB_LIBS = {
    "actix-web",
    "axum",
    "rocket",
    "warp",
    "hyper",
}

# Rust 算法学习项目特征
RUST_LEARNING_PATTERNS = {
    "algorithm",
    "leetcode",
    "binary-search",
    "dynamic-programming",
    "graph",
    "tree",
    "sorting",
}

RUST_MODULE_PATTERNS = {
    "mod.rs",
    "lib.rs",
    "main.rs",
}

# -------------------------
# Java Profile Rules
# -------------------------
JAVA_STDLIB_TARGETS = {
    "java.lang",
    "java.util",
    "java.io",
}

JAVA_WEB_LIBS = {
    "jakarta.servlet",
    "spring-core",
    "spring-web",
    "spring-boot",
}

JAVA_BUILD_TOOLS = {
    "maven",
    "gradle",
}

# ============================================================
# Profile Canonicalizer
# ============================================================

class ProfileCanonicalizer:
    """
    Infer semantic profiles with strict language ownership.

    Optimized with caching to avoid redundant computations.
    """

    def __init__(self):
        # profile_name -> (detector, owned_languages)
        self.rules = {
            # Python profiles
            "ml-python": (self._detect_ml_python, {LANG_PY}),
            "python-tool": (self._detect_python_tool, {LANG_PY}),
            "python-framework": (self._detect_python_framework, {LANG_PY}),

            # C profiles
            "system-c": (self._detect_system_c, {LANG_C, LANG_CPP}),
            "embedded-c": (self._detect_embedded_c, {LANG_C, LANG_CPP}),
            "cpp-competitive": (self._detect_cpp_competitive, {LANG_C, LANG_CPP}),
            "c-framework": (self._detect_c_framework, {LANG_C, LANG_CPP}),
            "riscv-os": (self._detect_riscv_os, {LANG_C, LANG_CPP}),

            # Rust profiles
            "rust-embedded": (self._detect_rust_embedded, {LANG_RUST}),
            "rust-web": (self._detect_rust_web, {LANG_RUST}),
            "rust-learning": (self._detect_rust_learning, {LANG_RUST}),
            "rust-framework": (self._detect_rust_framework, {LANG_RUST}),

            # Java profiles
            "java-web": (self._detect_java_web, {LANG_JAVA}),
            "java-lib": (self._detect_java_lib, {LANG_JAVA}),
            "java-framework": (self._detect_java_framework, {LANG_JAVA}),
        }

        # Cache for computed data to avoid redundant calculations
        self._cache = {
            'dominant_lang': None,
            'path_lower_set': None,
            'symbols_by_kind': None,
            'model_hash': None
        }

    # ========================================================
    # Entry
    # ========================================================

    def apply(self, model) -> None:
        """
        Apply profile detection with language ownership gate.

        Args:
            model: ProjectModel instance with finalized dependencies
        """
        if not model.deps_finalized:
            raise RuntimeError(
                "Profile detection requires finalized dependencies. "
                "Call model.finalize_dependencies() first."
            )

        # Check cache validity
        model_hash = self._compute_model_hash(model)
        if self._cache['model_hash'] != model_hash:
            # Invalidate cache if model changed
            self._cache = {
                'dominant_lang': None,
                'path_lower_set': None,
                'symbols_by_kind': None,
                'model_hash': model_hash
            }
            # Pre-compute and cache commonly used data
            self._cache['dominant_lang'] = self._infer_dominant_language(model)
            self._cache['path_lower_set'] = {u.path.lower() for u in model.units}
            self._cache['symbols_by_kind'] = self._group_symbols_by_kind(model)

        dominant_lang = self._cache['dominant_lang']

        # Step 1: Extract all dependency targets
        targets = self._extract_targets(model)

        # Step 2: Apply each profile rule with language gate
        detected = {}
        for name, (rule, owned_langs) in self.rules.items():
            # 🚫 Language ownership gate
            # A profile can only be active on languages it owns
            # 特殊处理：对于RISC-V和C语言项目，允许同时识别
            if dominant_lang and dominant_lang not in owned_langs:
                # 如果是riscv-os或c相关profile，且项目包含C语言，则允许检测
                if name in ["riscv-os", "system-c", "embedded-c", "c-framework"] and LANG_C in model.langs:
                    pass  # 允许检测
                else:
                    continue

            result = rule(model, targets, dominant_lang)
            if result:
                detected[name] = result

        # Step 3: Set profiles on model
        model.profiles = detected

        # Step 4: Set active profile (highest confidence)
        model.active_profile = self._pick_active_profile(detected)

    # ========================================================
    # Cache Helpers
    # ========================================================

    def _compute_model_hash(self, model) -> str:
        """
        Compute a simple hash of model state for cache invalidation.

        Args:
            model: ProjectModel instance

        Returns:
            Hash string representing model state
        """
        # Use a combination of unit count, symbol count, and dependency count
        # This is a lightweight check, not a cryptographic hash
        return f"{len(model.units)}-{len(model.symbols)}-{len(model._all_dep_keys)}"

    def _group_symbols_by_kind(self, model) -> Dict[str, Set[str]]:
        """
        Group symbols by their kind for fast lookup.

        Args:
            model: ProjectModel instance

        Returns:
            Dictionary mapping symbol kind to set of lowercase symbol names
        """
        symbols_by_kind = {}
        for s in model.symbols:
            if s.kind not in symbols_by_kind:
                symbols_by_kind[s.kind] = set()
            symbols_by_kind[s.kind].add(s.name.lower())
        return symbols_by_kind

    # ========================================================
    # Core Helpers
    # ========================================================

    def _infer_dominant_language(self, model) -> Optional[str]:
        """
        Determine dominant (target) language by unit count & role.

        The dominant language is the language with the most units,
        representing the primary target language of the project.
        """
        if not model.units:
            return None

        # Count units by language
        counter = Counter()
        for u in model.units:
            # Normalize language name (Rust -> RS)
            lang = u.lang
            if lang == LANG_RUST:
                lang = LANG_RS
            counter[lang] += 1

        if not counter:
            return None

        # Highest unit count wins
        dominant, _ = counter.most_common(1)[0]
        return dominant

    def _extract_targets(self, model) -> Set[str]:
        """Extract all dependency targets from the model."""
        targets = set()
        for _, _, target in model.dep_pool_items:
            # Extract library name from targets like [stdlib:py] or [numpy]
            if target.startswith("[") and target.endswith("]"):
                lib = target[1:-1]
                targets.add(lib.split(":")[0])
        return targets

    def _pick_active_profile(self, profiles: Dict) -> Optional[str]:
        """
        Pick the active profile from detected profiles.

        The profile with the highest confidence becomes active.
        """
        if not profiles:
            return None
        return max(
            profiles.items(),
            key=lambda x: x[1].get("confidence", 0.0)
        )[0]

    # ========================================================
    # Python Profiles
    # ========================================================

    def _detect_ml_python(self, model, targets, lang):
        """
        Detect ML Python profile.

        Rules:
        - Presence of core ML libraries (numpy, torch, tensorflow, etc.)
        - High confidence if multiple ML libs present
        """
        ml_found = ML_PYTHON_LIBS & targets
        if not ml_found:
            return None

        confidence = min(0.6 + len(ml_found) * 0.1, 0.95)

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:ml",
                "runtime:cpython",
                "stack:ml-python"
            ] + [f"lib:{x}" for x in sorted(ml_found)]
        }

    def _detect_python_framework(self, model, targets, lang):
        """
        Detect Python Framework profile.

        Rules:
        - Multi-module projects with layered architecture
        - Semantic class names indicating framework structure
        """
        confidence = 0.0
        signals = []

        if len(model.units) >= 8:
            confidence += 0.3
            signals.append("multi-module")

        modules = {u.module for u in model.units if u.module}
        if {"core", "analyzers"} <= modules:
            confidence += 0.3
            signals.append("layered-architecture")

        # Use cached symbols by kind
        class_names = self._cache.get('symbols_by_kind', {}).get('class', set())
        if any(k in name for k in ("model", "builder", "canon", "analysis") for name in class_names):
            confidence += 0.2
            signals.append("semantic-classes")

        if confidence < 0.45:
            return None

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:language-tooling",
                "runtime:cpython",
                "stack:python-framework"
            ],
            "signals": signals
        }

    # ========================================================
    # C / C++ Profiles
    # ========================================================

    def _detect_system_c(self, model, targets, lang):
        """
        Detect System C profile (OS / kernel related).

        Rules:
        - Presence of C stdlib targets
        - Multi-unit projects get higher confidence
        - Kernel-related unit names boost confidence
        """
        if not (C_STDLIB_TARGETS & targets):
            return None

        confidence = 0.4
        signals = []

        # Multi-unit bonus
        if len(model.units) > 10:
            confidence += 0.15
            signals.append("multi-unit")

        # Use cached path_lower_set
        path_lower = self._cache.get('path_lower_set', set())
        if KERNEL_C_SIGNALS & path_lower:
            confidence += 0.25
            signals.append("kernel-layout")

        confidence = min(confidence, 0.9)

        result = {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:system",
                "lang:c",
                "runtime:native",
            ]
        }

        if signals:
            result["signals"] = signals

        return result

    def _detect_embedded_c(self, model, targets, lang):
        """
        Detect Embedded C profile (newlib / RTOS).

        Rules:
        - Presence of embedded C libraries
        - Higher confidence with more embedded libs
        """
        embedded = EMBEDDED_C_LIBS & targets
        if not embedded:
            return None

        confidence = 0.6 + min(len(embedded) * 0.1, 0.3)

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:embedded",
                "lang:c",
                "runtime:baremetal",
            ] + [f"lib:{lib}" for lib in sorted(embedded)]
        }

    def _detect_cpp_competitive(self, model, targets, lang):
        """
        Detect C++ Competitive Programming profile.

        Rules:
        - Presence of C/C++ stdlib targets
        - File path patterns indicating competitive programming
        - Standard library headers usage
        - Competitive coding patterns
        """
        if not (C_STDLIB_TARGETS & targets):
            return None

        confidence = 0.0
        signals = []
        tags = ["lang:cpp", "domain:competitive-programming"]

        # Use cached path_lower_set
        path_lower = self._cache.get('path_lower_set', set())

        # Check for competitive programming patterns in file paths
        competitive_patterns_found = CPP_COMPETITIVE_PATTERNS & path_lower
        if competitive_patterns_found:
            confidence += 0.4
            signals.append("competitive-patterns")
            tags.append("purpose:icpc")

        # Check for standard library headers in dependencies
        std_headers_found = CPP_STD_HEADERS & targets
        if std_headers_found:
            confidence += 0.2
            signals.append("std-headers")

        # Check for bits/stdc++.h (common in competitive programming)
        for _, _, target in model.dep_pool_items:
            if "bits/stdc++.h" in target:
                confidence += 0.15
                signals.append("bits-stdcpp")
                break

        # Check for leetcode patterns
        if "leetcode" in path_lower:
            confidence += 0.25
            signals.append("leetcode-patterns")
            tags.extend(["pattern:leetcode", "difficulty:mixed"])

        # Multi-unit bonus (organized solutions)
        if len(model.units) > 5:
            confidence += 0.15
            signals.append("multi-unit")
            tags.append("module-organized")

        confidence = min(confidence, 0.95)

        if confidence < 0.4:
            return None

        return {
            "confidence": round(confidence, 2),
            "tags": tags,
            "signals": signals
        }

    def _detect_c_framework(self, model, targets, lang):
        """
        Detect C/C++ Framework profile.

        Rules:
        - General C/C++ framework detection
        - Multi-unit projects with linker dependencies
        """
        confidence = 0.5
        if any("ld" in (u.module or "") for u in model.units):
            confidence += 0.2

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:language-tooling",
                "runtime:native",
                "stack:c-framework"
            ]
        }

    def _detect_riscv_os(self, model, targets, lang):
        """
        Detect RISC-V OS profile.

        Rules:
        - Presence of RISC-V runtime (riscv-rt)
        - Linker script with RISC-V specific sections
        - Assembly files with RISC-V instructions (ecall, mret, sret, CSR)
        - RISC-V specific symbols (_start, trap_vector, etc.)
        """
        confidence = 0.0
        signals = []
        tags = ["lang:c", "domain:os", "arch:riscv"]

        # Check for RISC-V runtime
        if "riscv-rt" in targets:
            confidence += 0.3
            signals.append("riscv-rt")

        # Check for embedded C libraries
        embedded_libs = EMBEDDED_C_LIBS & targets
        if embedded_libs:
            confidence += 0.2
            signals.append(f"embedded-libs({len(embedded_libs)})")

        # Check for linker scripts
        has_ld = any(u.path.endswith(".ld") or u.path.endswith(".lds") for u in model.units)
        if has_ld:
            confidence += 0.15
            signals.append("linker-script")

        # Check for RISC-V specific symbols
        riscv_symbols = {"_start", "trap_vector", "trap_entry", "irq_handler"}
        found_riscv_syms = riscv_symbols & {s.name for s in model.symbols}
        if found_riscv_syms:
            confidence += 0.2
            signals.append(f"riscv-symbols({len(found_riscv_syms)})")

        # Check for RISC-V specific unit paths
        riscv_paths = sum(1 for u in model.units if "riscv" in u.path.lower())
        if riscv_paths > 0:
            confidence += 0.15
            signals.append(f"riscv-paths({riscv_paths})")

        confidence = min(confidence, 0.95)

        if confidence < 0.4:
            return None

        result = {
            "confidence": round(confidence, 2),
            "tags": tags + [f"lib:{lib}" for lib in sorted(embedded_libs)],
            "signals": signals
        }

        return result

    # ========================================================
    # Rust Profiles
    # ========================================================

    def _detect_rust_embedded(self, model, targets, lang):
        """
        Detect Rust Embedded profile (no_std / embedded-hal).

        Rules:
        - Presence of embedded Rust libraries
        - Higher confidence with more embedded libs
        """
        embedded = RUST_EMBEDDED_LIBS & targets
        if not embedded:
            return None

        confidence = 0.65 + min(len(embedded) * 0.1, 0.3)

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:embedded",
                "lang:rust",
                "runtime:no_std",
            ] + [f"lib:{lib}" for lib in sorted(embedded)]
        }

    def _detect_rust_web(self, model, targets, lang):
        """
        Detect Rust Web Backend profile.

        Rules:
        - Presence of Rust web frameworks
        - Higher confidence with more web libs
        """
        web = RUST_WEB_LIBS & targets
        if not web:
            return None

        confidence = 0.6 + min(len(web) * 0.1, 0.3)

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:web-backend",
                "lang:rust",
                "runtime:native",
            ] + [f"lib:{lib}" for lib in sorted(web)]
        }

    def _detect_rust_learning(self, model, targets, lang):
        """
        Detect Rust Learning/Algorithm project profile.

        Rules:
        - Presence of Rust stdlib targets
        - File path patterns indicating algorithm learning
        - Module structure (mod.rs, lib.rs, main.rs)
        - No heavy framework dependencies
        - Multiple main.rs files (multiple small projects)
        - Project name or directory containing 'learn', 'tutorial', 'example'
        - Algorithm-related function names
        - Learning-related project names (hello_world, variables, adder)
        """
        if not (RUST_STDLIB_TARGETS & targets):
            return None

        confidence = 0.0
        signals = []
        tags = ["lang:rust", "purpose:learning", "domain:algorithms"]

        # Use cached path_lower_set
        path_lower = self._cache.get('path_lower_set', set())

        # Check for learning patterns in file paths
        learning_patterns_found = RUST_LEARNING_PATTERNS & path_lower
        if learning_patterns_found:
            confidence += 0.3
            signals.append("learning-patterns")

        # Check for Rust module structure
        module_patterns_found = RUST_MODULE_PATTERNS & path_lower
        if module_patterns_found:
            confidence += 0.25
            signals.append("mod-structure")
            if "mod.rs" in module_patterns_found:
                tags.append("ecosystem:cargo")

        # Check for stdlib presence
        if RUST_STDLIB_TARGETS & targets:
            confidence += 0.2
            signals.append("rust-stdlib")
            tags.append("build:rustc")

        # Multi-unit bonus
        if len(model.units) > 5:
            confidence += 0.15
            signals.append("multi-unit")

        # No heavy frameworks (web, embedded)
        if not (RUST_WEB_LIBS & targets) and not (RUST_EMBEDDED_LIBS & targets):
            confidence += 0.1
            signals.append("pure-learning")

        # Check for multiple main.rs files (indicates multiple small projects)
        main_rs_count = sum(1 for path in path_lower if path.endswith("main.rs"))
        if main_rs_count >= 2:
            confidence += 0.15
            signals.append(f"multiple-main-rs({main_rs_count})")

        # Check for learning-related directory names
        learning_dirs = {"learn", "tutorial", "example", "demo", "test", "practice", "exercise"}
        found_learning_dirs = any(d in path for d in learning_dirs for path in path_lower)
        if found_learning_dirs:
            confidence += 0.1
            signals.append("learning-directory")

        # Check for algorithm-related function names
        algo_keywords = {"sort", "search", "find", "tree", "graph", "heap", "stack", "queue", 
                         "hash", "binary", "dynamic", "greedy", "recursive", "iterative"}
        # Use cached symbols_by_kind
        symbols_by_kind = self._cache.get('symbols_by_kind', {})
        func_names = symbols_by_kind.get('func', set())
        found_algo_funcs = func_names & algo_keywords
        if found_algo_funcs:
            confidence += 0.1 * min(len(found_algo_funcs), 3)  # Max 0.3 bonus
            signals.append(f"algo-functions({len(found_algo_funcs)})")

        # Check for learning-related project names
        learning_projects = {"hello_world", "variables", "adder", "hello_package", "minigrep"}
        found_learning_projects = any(proj in path_lower for proj in learning_projects)
        if found_learning_projects:
            confidence += 0.1
            signals.append("learning-project-names")

        # Check for learning-related symbols
        learning_symbols = {"it_works", "test", "example", "demo"}
        all_symbol_names = set()
        for symbol_set in symbols_by_kind.values():
            all_symbol_names.update(symbol_set)
        found_learning_symbols = all_symbol_names & learning_symbols
        if found_learning_symbols:
            confidence += 0.05
            signals.append("learning-symbols")

        confidence = min(confidence, 0.95)

        if confidence < 0.4:
            return None

        return {
            "confidence": round(confidence, 2),
            "tags": tags,
            "signals": signals
        }

    def _detect_rust_framework(self, model, targets, lang):
        """
        Detect Rust Framework profile.

        Rules:
        - General Rust framework detection
        - Multi-unit projects
        """
        confidence = 0.5
        if len(model.units) >= 5:
            confidence += 0.2

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:language-tooling",
                "runtime:rust",
                "stack:rust-framework"
            ]
        }

    # ========================================================
    # Java Profiles
    # ========================================================

    def _detect_java_web(self, model, targets, lang):
        """
        Detect Java Web Backend profile (Spring / Jakarta).

        Rules:
        - Presence of Java web frameworks
        - Higher confidence with more web libs
        """
        web = JAVA_WEB_LIBS & targets
        if not web:
            return None

        confidence = 0.6 + min(len(web) * 0.1, 0.3)

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:web-backend",
                "lang:java",
                "runtime:jvm",
            ] + [f"lib:{lib}" for lib in sorted(web)]
        }

    def _detect_java_lib(self, model, targets, lang):
        """
        Detect Java Library / Utility profile.

        Rules:
        - Presence of Java stdlib targets
        - Multi-unit projects (>5 units)
        """
        if JAVA_STDLIB_TARGETS & targets and len(model.units) > 5:
            return {
                "confidence": 0.45,
                "tags": [
                    "domain:library",
                    "lang:java",
                    "runtime:jvm",
                ]
            }

        return None

    def _detect_java_framework(self, model, targets, lang):
        """
        Detect Java Framework profile.

        Rules:
        - General Java framework detection
        """
        confidence = 0.5
        return {
            "confidence": confidence,
            "tags": [
                "domain:language-tooling",
                "runtime:jvm",
                "stack:java-framework"
            ]
        }

    def _detect_python_tool(self, targets: Set[str], model) -> Optional[Dict]:
        """
        Improved Python Tool profile detection with semantic weighting.
        
        Added language conflict detection to avoid misidentifying
        Rust/C++ projects as python-tool.
        """
        # Language conflict check: if project has non-Python languages,
        # only detect python-tool if Python is the dominant language
        if model.langs and len(model.langs) > 1:
            if "PY" not in model.langs:
                return None
            # Count units by language
            lang_counts = {}
            for unit in model.units:
                lang_counts[unit.lang] = lang_counts.get(unit.lang, 0) + 1
            # Python must be the dominant language (> 50%)
            py_count = lang_counts.get("PY", 0)
            total_count = sum(lang_counts.values())
            if py_count / total_count <= 0.5:
                return None

        tool_libs_found = PYTHON_TOOL_LIBS & targets
        if not tool_libs_found:
            return None

        confidence = 0.0
        reasons = []

        # 1️⃣ stdlib is a strong base signal
        if "stdlib" in tool_libs_found:
            confidence += 0.4
            reasons.append("stdlib")

        # 2️⃣ additional tooling libs (weak additive)
        extra_tools = tool_libs_found - {"stdlib"}
        confidence += min(len(extra_tools) * 0.05, 0.15)

        # 3️⃣ language purity bonus
        if model.langs == {"PY"}:
            confidence += 0.15
            reasons.append("pure-python")

        # 4️⃣ entry point bonus
        has_entry = any(
            s.kind == "func" and s.attrs.get("entry") == "true"
            for s in model.symbols
        )
        if has_entry:
            confidence += 0.1
            reasons.append("entry-point")

        # 5️⃣ project scale sanity (not a single-file script)
        if len(model.units) >= 5:
            confidence += 0.1
            reasons.append("multi-unit")

        # 6️⃣ conflict penalty (ML / heavy frameworks present)
        if ML_PYTHON_LIBS & targets:
            confidence -= 0.25
            reasons.append("ml-conflict")

        confidence = max(0.0, min(round(confidence, 2), 0.95))

        if confidence < 0.3:
            return None

        tags = [
            "domain:tooling",
            "runtime:cpython",
            "stack:python-tool",
        ] + [f"lib:{lib}" for lib in sorted(tool_libs_found)]

        return {
            "confidence": confidence,
            "tags": tags,
            "signals": reasons
        }

    def _detect_python_tool(self, model, targets, lang):
        """
        Detect Python Tool profile.

        Rules:
        - Small, flat projects with tooling libraries
        - Entry point detection
        - Note: Language ownership is enforced at apply() level
        """
        # Only small, flat projects
        if len(model.units) > 5:
            return None

        confidence = 0.4
        signals = ["small-project"]

        has_entry = any(
            s.kind == "func" and s.attrs.get("entry") == "true"
            for s in model.symbols
        )
        if has_entry:
            confidence += 0.2
            signals.append("entry-point")

        return {
            "confidence": round(confidence, 2),
            "tags": [
                "domain:tooling",
                "runtime:cpython",
                "stack:python-tool"
            ],
            "signals": signals
        }
