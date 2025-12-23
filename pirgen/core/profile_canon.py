# core/profile_canon.py
"""
Profile Canonicalization (Profile-Aware Semantic IR)

Analyze project dependencies and file structure to infer high-level
semantic profiles (e.g., ml-python, web-backend, etc.)
"""

from typing import Dict, List, Set, Optional
from collections import defaultdict

# -------------------------
# Profile Rules
# -------------------------

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

# -------------------------
# Profile Canonicalizer
# -------------------------
class ProfileCanonicalizer:
    """
    Analyze project dependencies and infer semantic profiles.

    Profiles are non-authoritative, derived metadata that provide
    high-level semantic understanding of a project.
    """

    def __init__(self):
        self.rules = {
            # Python
            "ml-python": self._detect_ml_python,
            "python-tool": self._detect_python_tool,

            # C
            "system-c": self._detect_system_c,
            "embedded-c": self._detect_embedded_c,

            # Rust
            "rust-embedded": self._detect_rust_embedded,
            "rust-web": self._detect_rust_web,

            # Java
            "java-web": self._detect_java_web,
            "java-lib": self._detect_java_lib,
        }

    def apply(self, model) -> None:
        """
        Apply profile detection to a ProjectModel instance.

        Args:
            model: ProjectModel instance with finalized dependencies
        """
        if not model.deps_finalized:
            raise RuntimeError(
                "Profile detection requires finalized dependencies. "
                "Call model.finalize_dependencies() first."
            )

        # Extract all dependency targets
        all_targets = self._extract_all_targets(model)

        # Apply each profile rule
        detected_profiles = {}
        for profile_name, rule_func in self.rules.items():
            result = rule_func(all_targets, model)
            if result:
                detected_profiles[profile_name] = result

        # Set profiles on model
        model.profiles = detected_profiles

        # Set active profile (highest confidence)
        if detected_profiles:
            # Sort by confidence, descending
            sorted_profiles = sorted(
                detected_profiles.items(),
                key=lambda x: x[1].get("confidence", 0.0),
                reverse=True
            )
            model.active_profile = sorted_profiles[0][0]
        else:
            model.active_profile = None

    def _extract_all_targets(self, model) -> Set[str]:
        """Extract all dependency targets from the model."""
        targets = set()
        for _, verb, target in model.dep_pool_items:
            # Extract library name from targets like [stdlib:py] or [numpy]
            if target.startswith("[") and target.endswith("]"):
                lib_name = target[1:-1]
                # Handle normalized targets like "stdlib:py"
                if ":" in lib_name:
                    # For stdlib:py, add "stdlib" to targets
                    # This allows matching against PYTHON_TOOL_LIBS
                    prefix = lib_name.split(":")[0]
                    targets.add(prefix)
                else:
                    targets.add(lib_name)
        return targets

    def _detect_ml_python(self, targets: Set[str], model) -> Optional[Dict]:
        """
        Detect ML Python profile.

        Rules:
        - Presence of core ML libraries (numpy, torch, tensorflow, etc.)
        - High confidence if multiple ML libs present
        """
        ml_libs_found = ML_PYTHON_LIBS & targets

        if not ml_libs_found:
            return None

        # Calculate confidence based on number of ML libraries found
        confidence = min(0.5 + len(ml_libs_found) * 0.1, 1.0)

        # Build tags
        tags = [
            "domain:ml",
            "runtime:cpython",
            "stack:ml-python",
        ]

        # Add specific library tags
        for lib in sorted(ml_libs_found):
            tags.append(f"lib:{lib}")

        return {
            "confidence": round(confidence, 2),
            "tags": tags
        }

    # -------------------------
    # C Profile Detectors
    # -------------------------
    def _detect_system_c(self, targets: Set[str], model) -> Optional[Dict]:
        """
        Detect System C profile (OS / kernel related).

        Rules:
        - Presence of C stdlib targets
        - Multi-unit projects get higher confidence
        - Kernel-related unit names boost confidence
        """
        if "C" not in model.langs:
            return None

        if not (C_STDLIB_TARGETS & targets):
            return None

        confidence = 0.4
        signals = []

        # Multi-unit bonus
        if len(model.units) > 10:
            confidence += 0.15
            signals.append("multi-unit")

        # Directory semantic signals
        unit_names = {u.path.lower() for u in model.units}
        if KERNEL_C_SIGNALS & unit_names:
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

    def _detect_embedded_c(self, targets: Set[str], model) -> Optional[Dict]:
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

    # -------------------------
    # Rust Profile Detectors
    # -------------------------
    def _detect_rust_embedded(self, targets: Set[str], model) -> Optional[Dict]:
        """
        Detect Rust Embedded profile (no_std / embedded-hal).

        Rules:
        - Presence of embedded Rust libraries
        - Higher confidence with more embedded libs
        """
        if "Rust" not in model.langs:
            return None

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

    def _detect_rust_web(self, targets: Set[str], model) -> Optional[Dict]:
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

    # -------------------------
    # Java Profile Detectors
    # -------------------------
    def _detect_java_web(self, targets: Set[str], model) -> Optional[Dict]:
        """
        Detect Java Web Backend profile (Spring / Jakarta).

        Rules:
        - Presence of Java web frameworks
        - Higher confidence with more web libs
        """
        if "JAVA" not in model.langs:
            return None

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

    def _detect_java_lib(self, targets: Set[str], model) -> Optional[Dict]:
        """
        Detect Java Library / Utility profile.

        Rules:
        - Presence of Java stdlib targets
        - Multi-unit projects (>5 units)
        """
        if "JAVA" not in model.langs:
            return None

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

    def _detect_python_tool(self, targets: Set[str], model) -> Optional[Dict]:
        """
        Improved Python Tool profile detection with semantic weighting.
        """

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
