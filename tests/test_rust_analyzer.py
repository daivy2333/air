"""Tests for Rust analyzer.

Tests cover:
- async fn detection
- Generic functions
- impl blocks (impl Struct and impl Trait for Struct)
- Complex use paths and grouping
"""

import tempfile
import os
import pytest
from pirgen.analyzers.rust_analyzer import RustAnalyzer
from pirgen.core.project_model import ProjectModel


class TestRustAnalyzer:
    def setup_method(self):
        self.analyzer = RustAnalyzer()

    def _analyze_file(self, content: str) -> ProjectModel:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        model = ProjectModel("test", "/tmp", "rust")
        uid = model.add_unit(path, "Rust", "src")
        self.analyzer.analyze(path, uid, model)

        os.unlink(path)
        return model

    def test_basic_function_detection(self):
        content = """
fn hello() {
    println!("hello");
}

fn add(a: i32, b: i32) -> i32 {
    a + b
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "hello" in symbols
        assert "add" in symbols

    def test_public_function(self):
        content = """
pub fn public_api() {
}

fn private_func() {
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "public_api" in symbols
        assert "private_func" in symbols

    def test_async_function(self):
        content = """
async fn fetch_data() {
}

pub async fn process_request() -> Result<(), Error> {
}

async fn compute_async(x: i32) -> i32 {
    x + 1
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "fetch_data" in symbols
        assert "process_request" in symbols
        assert "compute_async" in symbols

    def test_generic_function(self):
        content = """
fn identity<T>(x: T) -> T {
    x
}

pub fn combine<T, U>(a: T, b: U) -> (T, U) {
    (a, b)
}

fn process<'a, T>(data: &'a T) {
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "identity" in symbols
        assert "combine" in symbols
        assert "process" in symbols

    def test_struct_detection(self):
        content = """
struct Point {
    x: i32,
    y: i32,
}

pub struct Config {
    name: String,
}

struct EmptyStruct;
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        kinds = {s.name: s.kind for s in model.symbols}
        
        assert "Point" in symbols
        assert kinds["Point"] == "struct"
        assert "Config" in symbols
        assert kinds["Config"] == "struct"
        assert "EmptyStruct" in symbols

    def test_enum_detection(self):
        content = """
enum Status {
    Ok,
    Error,
}

pub enum Color {
    Red,
    Green,
    Blue,
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        kinds = {s.name: s.kind for s in model.symbols}
        
        assert "Status" in symbols
        assert kinds["Status"] == "enum"
        assert "Color" in symbols
        assert kinds["Color"] == "enum"

    def test_trait_detection(self):
        content = """
trait Drawable {
    fn draw(&self);
}

pub trait Serializable {
    fn serialize(&self) -> String;
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        kinds = {s.name: s.kind for s in model.symbols}
        
        assert "Drawable" in symbols
        assert kinds["Drawable"] == "trait"
        assert "Serializable" in symbols
        assert kinds["Serializable"] == "trait"

    def test_impl_block_basic(self):
        content = """
struct Calculator;

impl Calculator {
    fn new() -> Self {
        Self
    }
    
    fn add(&self, a: i32, b: i32) -> i32 {
        a + b
    }
}
"""
        model = self._analyze_file(content)
        symbols = model.symbols
        
        impl_syms = [s for s in symbols if s.kind == "impl"]
        assert len(impl_syms) == 1
        assert impl_syms[0].name == "Calculator"

    def test_impl_trait_for_struct(self):
        content = """
struct MyType;
struct OtherType;

impl Display for MyType {
    fn fmt(&self, f: &mut Formatter) -> Result {
        write!(f, "MyType")
    }
}

impl Debug for OtherType {
    fn fmt(&self, f: &mut Formatter) -> Result {
        write!(f, "OtherType {{ }}")
    }
}
"""
        model = self._analyze_file(content)
        symbols = model.symbols
        
        impl_syms = [s for s in symbols if s.kind == "impl"]
        impl_names = [s.name for s in impl_syms]
        
        assert "MyType" in impl_names
        assert "OtherType" in impl_names
        assert len(impl_syms) == 2

    def test_impl_duplicate_handling(self):
        content = """
struct Point;

impl Point {
    fn method1() {}
}

impl Point {
    fn method2() {}
}
"""
        model = self._analyze_file(content)
        symbols = model.symbols
        
        impl_syms = [s for s in symbols if s.kind == "impl"]
        assert len(impl_syms) == 1
        assert impl_syms[0].name == "Point"

    def test_main_entry_point(self):
        content = """
fn main() {
    println!("Hello");
}
"""
        model = self._analyze_file(content)
        
        main_sym = [s for s in model.symbols if s.name == "main"]
        assert len(main_sym) == 1
        assert main_sym[0].attrs.get("entry") == "true"

    def test_use_std(self):
        content = """
use std::collections::HashMap;
use std::io::Read;
use std::sync::Mutex;
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[std::collections::HashMap]" in targets
        assert "[std::io::Read]" in targets
        assert "[std::sync::Mutex]" in targets

    def test_use_crate(self):
        content = """
use crate::module::function;
use crate::types::MyType;
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[crate::module::function]" in targets
        assert "[crate::types::MyType]" in targets

    def test_use_relative(self):
        content = """
use self::local_module::Item;
use super::parent_module::Type;
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[self::local_module::Item]" in targets
        assert "[super::parent_module::Type]" in targets

    def test_use_external(self):
        content = """
use serde::Serialize;
use tokio::runtime::Runtime;
use rand::Rng;
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[serde::Serialize]" in targets
        assert "[tokio::runtime::Runtime]" in targets
        assert "[rand::Rng]" in targets

    def test_use_grouped_imports(self):
        content = """
use std::collections::{HashMap, HashSet, VecDeque};
use std::io::{Read, Write, BufReader};
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[std::collections::{HashMap, HashSet, VecDeque}]" in targets
        assert "[std::io::{Read, Write, BufReader}]" in targets

    def test_use_complex_path(self):
        content = """
use crate::deep::nested::module::Type;
use std::sync::atomic::AtomicUsize;
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert any("deep::nested::module::Type" in t for t in targets)
        assert any("sync::atomic::AtomicUsize" in t for t in targets)

    def test_use_with_alias(self):
        content = """
use std::collections::HashMap as Map;
use serde::Serialize as Ser;
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        assert len(dep_items) >= 2

    def test_use_glob(self):
        content = """
use std::io::prelude::*;
use crate::utils::*;
"""
        model = self._analyze_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[std::io::prelude::*]" in targets
        assert "[crate::utils::*]" in targets

    def test_empty_file(self):
        content = ""
        model = self._analyze_file(content)
        assert len(model.symbols) == 0

    def test_only_comments(self):
        content = """
// This is a comment
/// Doc comment
//! Module doc
"""
        model = self._analyze_file(content)
        assert len(model.symbols) == 0

    def test_nested_blocks(self):
        content = """
fn outer() {
    let inner = || {
        // closure
    };
}

impl Outer {
    fn method(&self) {
        // method body
    }
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        assert "outer" in symbols
        assert "Outer" in symbols

    def test_function_without_body_not_detected(self):
        content = """
fn declared_function();

fn implemented_function() {
}
"""
        model = self._analyze_file(content)
        symbols = [s.name for s in model.symbols]
        
        assert "declared_function" not in symbols
        assert "implemented_function" in symbols