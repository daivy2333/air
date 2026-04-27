"""Tests for Python analyzer.

Tests cover:
- try-except ImportError patterns
- TYPE_CHECKING blocks
- Nested symbols (methods, inner classes)
- Top-level imports and symbols
"""

import tempfile
import os
import pytest
from pirgen.analyzers.python_analyzer import PythonAnalyzer
from pirgen.core.project_model import ProjectModel


class TestPythonAnalyzer:
    def setup_method(self):
        self.analyzer = PythonAnalyzer()

    def _analyze_file(self, content: str) -> ProjectModel:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        model = ProjectModel("test", "/tmp", "py")
        uid = model.add_unit(path, "PY", "src")
        self.analyzer.analyze(path, uid, model)

        os.unlink(path)
        return model

    def test_basic_function_detection(self):
        content = """
def hello():
    pass

def world(name):
    return name
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "hello" in symbols
        assert "world" in symbols

    def test_async_function_detection(self):
        content = """
async def fetch_data():
    pass

async def process():
    return 42
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "fetch_data" in symbols
        assert "process" in symbols

    def test_class_detection(self):
        content = """
class Calculator:
    pass

class MyClass(BaseClass):
    def method(self):
        pass
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "Calculator" in symbols
        assert "MyClass" in symbols

    def test_private_symbols_skipped(self):
        content = """
def _private_func():
    pass

def public_func():
    pass

class _PrivateClass:
    pass

class PublicClass:
    pass
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "_private_func" not in symbols
        assert "public_func" in symbols
        assert "_PrivateClass" not in symbols
        assert "PublicClass" in symbols

    def test_nested_symbols(self):
        content = """
class OuterClass:
    def outer_method(self):
        pass
    
    class InnerClass:
        def inner_method(self):
            pass
    
    def another_method(self):
        def local_func():
            pass
        return local_func

def outer_func():
    def nested_func():
        pass
    return nested_func
"""
        model = self._analyze_file(content)
        symbols = model.symbols
        
        symbol_names = [s.name for s in symbols]
        assert "OuterClass" in symbol_names
        assert "outer_func" in symbol_names
        
        nested_symbols = [s for s in symbols if s.attrs.get("nested") == "true"]
        nested_names = [s.name for s in nested_symbols]
        assert "outer_method" in nested_names
        assert "InnerClass" in nested_names
        assert "inner_method" in nested_names
        assert "another_method" in nested_names
        assert "nested_func" in nested_names

    def test_type_checking_imports(self):
        content = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict
    from collections.abc import Iterable
    import os as operating_system

def normal_import():
    import sys
    return sys
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        type_checking_deps = [d for d in dep_items if d[1] == "import_type_checking"]
        
        assert len(type_checking_deps) >= 1
        targets = [d[2] for d in type_checking_deps]
        assert "[typing]" in targets or "[List]" in targets

    def test_type_checking_attribute_style(self):
        content = """
import typing

if typing.TYPE_CHECKING:
    from some_module import SomeClass

def func():
    pass
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        type_checking_deps = [d for d in dep_items if d[1] == "import_type_checking"]
        assert len(type_checking_deps) >= 1

    def test_regular_import(self):
        content = """
import os
import sys
from collections import defaultdict
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[os]" in targets
        assert "[sys]" in targets
        assert "[collections]" in targets

    def test_relative_import(self):
        content = """
from .utils import helper
from ..parent import ParentClass
from .submodule import func
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        relative_deps = [d for d in dep_items if d[1] == "import_relative"]
        
        assert len(relative_deps) >= 1
        targets = [d[2] for d in relative_deps]
        assert "[.utils]" in targets or "[..parent]" in targets

    def test_import_classification_std(self):
        content = """
import os
import sys
import re
import ast
import typing
import dataclasses
import abc
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        std_deps = [d for d in dep_items if d[1] == "import_std"]
        assert len(std_deps) >= 7

    def test_import_classification_private(self):
        content = """
import _private_module
from _internal import something
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        private_deps = [d for d in dep_items if d[1] == "import_private"]
        assert len(private_deps) >= 1

    def test_import_classification_external(self):
        content = """
import numpy
import pandas
from requests import get
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        external_deps = [d for d in dep_items if d[1] == "import_external"]
        assert len(external_deps) >= 3

    def test_main_entry_point(self):
        content = """
def main():
    pass

def other():
    pass
"""
        model = self._analyze_file(content)
        
        main_sym = [s for s in model.symbols if s.name == "main"]
        assert len(main_sym) == 1
        assert main_sym[0].attrs.get("entry") == "true"
        
        other_sym = [s for s in model.symbols if s.name == "other"]
        assert len(other_sym) == 1
        assert other_sym[0].attrs.get("entry") is None

    def test_syntax_error_graceful_handling(self):
        content = """
this is not valid python syntax
"""
        model = self._analyze_file(content)
        assert len(model.symbols) == 0

    def test_empty_file(self):
        content = ""
        model = self._analyze_file(content)
        assert len(model.symbols) == 0

    def test_only_comments(self):
        content = """
# This is a comment
# Another comment
"""
        model = self._analyze_file(content)
        assert len(model.symbols) == 0

    def test_module_level_import_from(self):
        content = """
from module.submodule import ClassA, ClassB, func_c
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        assert "[module.submodule]" in targets

    def test_import_with_alias(self):
        content = """
import numpy as np
import pandas as pd
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        assert "[numpy]" in targets
        assert "[pandas]" in targets

    def test_dunder_main_pattern(self):
        content = """
if __name__ == "__main__":
    main()
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert len(symbols) == 0