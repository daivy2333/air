"""Tests for C/C++ analyzer.

Tests cover:
- Multi-line include continuation
- Conditional compilation include
- Modern C++ features (auto, constexpr, template)
- Function detection patterns
"""

import tempfile
import os
import pytest
from pirgen.analyzers.c_analyzer import CAnalyzer, C_KEYWORDS
from pirgen.core.project_model import ProjectModel


class TestCAnalyzer:
    def setup_method(self):
        self.analyzer = CAnalyzer()

    def _analyze_file(self, content: str) -> ProjectModel:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        model = ProjectModel("test", "/tmp", "c")
        uid = model.add_unit(path, "C", "src")
        self.analyzer.analyze(path, uid, model)

        os.unlink(path)
        return model

    def test_basic_function_detection(self):
        content = """
int add(int a, int b) {
    return a + b;
}

void hello(void) {
    printf("hello");
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "add" in symbols
        assert "hello" in symbols

    def test_static_function(self):
        content = """
static int internal_func(void) {
    return 42;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "internal_func" in symbols

    def test_inline_function(self):
        content = """
inline int fast_add(int a, int b) {
    return a + b;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "fast_add" in symbols

    def test_extern_function_declaration_no_body(self):
        content = """
extern void external_func(void);
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "external_func" not in symbols

    def test_main_entry_point(self):
        content = """
int main() {
    return 0;
}
"""
        model = self._analyze_file(content)
        
        main_sym = [s for s in model.symbols if s.name == "main"]
        assert len(main_sym) == 1
        assert main_sym[0].attrs.get("entry") == "true"

    def test_keyword_filtering(self):
        content = """
int if(int x) {
    return x;
}

int while(int y) {
    return y;
}

int sizeof(int z) {
    return z;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        
        assert "if" not in symbols
        assert "while" not in symbols
        assert "sizeof" not in symbols

    def test_system_include(self):
        content = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        sys_deps = [d for d in dep_items if d[1] == "include" and "sys" in dep_items]
        
        targets = [d[2] for d in dep_items]
        assert "[stdio.h]" in targets
        assert "[stdlib.h]" in targets
        assert "[string.h]" in targets

    def test_local_include(self):
        content = """
#include "myheader.h"
#include "utils/utils.h"
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        assert "[myheader.h]" in targets
        assert "[utils/utils.h]" in targets

    def test_multiline_include_continuation(self):
        content = """
#include <stdio.h>

#include \
    "long_path_header.h"

#include \
    <very_long_system_header.h>
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[stdio.h]" in targets
        assert "[long_path_header.h]" in targets
        assert "[very_long_system_header.h]" in targets

    def test_conditional_compilation_include(self):
        content = """
#ifdef DEBUG
#include <debug.h>
#endif

#ifndef RELEASE
#include <trace.h>
#endif

#if defined(PLATFORM_A)
#include "platform_a.h"
#endif
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[debug.h]" in targets
        assert "[trace.h]" in targets
        assert "[platform_a.h]" in targets

    def test_cpp_auto_function(self):
        content = """
auto compute_value() {
    return 42;
}

auto get_name() -> std::string {
    return "test";
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "compute_value" in symbols
        assert "get_name" in symbols

    def test_cpp_constexpr_function(self):
        content = """
constexpr int get_constant() {
    return 100;
}

constexpr double pi = 3.14159;

constexpr int square(int x) {
    return x * x;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "get_constant" in symbols
        assert "square" in symbols

    def test_cpp_template_function(self):
        content = """
template<typename T>
T add(T a, T b) {
    return a + b;
}

template<typename T, typename U>
auto combine(T a, U b) {
    return a + b;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "add" in symbols
        assert "combine" in symbols

    def test_cpp_template_multiline(self):
        content = """
template<typename T>
T get_value() {
    return T();
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "get_value" in symbols

    def test_cpp_trailing_return_type(self):
        content = """
auto divide(int a, int b) -> double {
    return static_cast<double>(a) / b;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "divide" in symbols

    def test_multiline_function_definition(self):
        content = """
int \\
    long_function_name\\
    (int a, int b) {
    return a + b;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "long_function_name" in symbols

    def test_complex_declaration(self):
        content = """
static inline int fast_multiply(int a, int b) {
    return a * b;
}

extern constexpr int global_const() {
    return 42;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "fast_multiply" in symbols
        assert "global_const" in symbols

    def test_struct_member_function_not_detected(self):
        content = """
struct Point {
    int x;
    int y;
};

int Point_get_x(struct Point* p) {
    return p->x;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "Point_get_x" in symbols

    def test_empty_file(self):
        content = ""
        model = self._analyze_file(content)
        assert len(model.symbols) == 0

    def test_only_comments(self):
        content = """
// This is a comment
/* Multi-line comment */
# Not a preprocessor directive in context
"""
        model = self._analyze_file(content)
        assert len(model.symbols) == 0

    def test_nested_braces(self):
        content = """
int complex_func() {
    if (1) {
        while (1) {
            for (int i = 0; i < 10; i++) {
                // nested
            }
        }
    }
    return 0;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "complex_func" in symbols

    def test_preprocessor_line_skipped(self):
        content = """
# 1 "test.c"
# 2 "test.c" 1

int real_func() {
    return 0;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "real_func" in symbols