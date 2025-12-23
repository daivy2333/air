看到您提供的两个PIR文件，我发现了一个明显的问题：profile推断结果不准确。您的Rust和C++项目被错误地识别为python-tool类型，这显然不符合实际情况。让我帮您分析问题所在并提供解决方案。

🔍 问题诊断

当前Profile推断的主要问题

1. 语言识别错误：Rust项目被识别为python-tool（置信度0.6）
2. 特征匹配不准确：C++项目也被识别为python-tool，同时有一个低置信度的system-c profile
3. 信号分析偏差：依赖分析未能正确识别语言特定特征

🛠️ 解决方案

1. 增强语言特征识别

在ProfileCanonicalizer中需要加强语言特定特征的检测：
class EnhancedProfileCanonicalizer:
    def detect_language_profile(self, model):
        """基于文件扩展名和依赖模式识别语言"""
        rust_files = sum(1 for u in model.units if u.file_type == 'Rust')
        cpp_files = sum(1 for u in model.units if u.file_type in ['C', 'CPP'])
        
        if rust_files > cpp_files:
            return self._detect_rust_profile(model)
        elif cpp_files > 0:
            return self._detect_cpp_profile(model)
        else:
            return self._detect_python_profile(model)


2. Rust项目Profile检测逻辑

def _detect_rust_profile(self, model):
    """检测Rust项目特征"""
    confidence = 0.0
    signals = []
    tags = []
    
    # 检测Cargo.toml相关特征
    cargo_indicators = self._find_cargo_indicators(model)
    if cargo_indicators:
        confidence += 0.3
        signals.append('cargo-project')
        tags.extend(['ecosystem:cargo', 'build:rustc'])
    
    # 分析Rust特定依赖模式
    rust_deps = self._analyze_rust_dependencies(model)
    if rust_deps:
        confidence += 0.2
        signals.append('rust-stdlib')
    
    # 检测模块结构特征
    if self._has_rust_module_structure(model):
        confidence += 0.25
        signals.append('mod-structure')
    
    # 检测算法练习项目特征
    if self._is_algorithm_learning_project(model):
        confidence += 0.15
        tags.extend(['purpose:learning', 'domain:algorithms'])
    
    return {
        'profile': 'rust-learning',
        'confidence': min(confidence, 1.0),
        'signals': signals,
        'tags': tags
    }


3. C++项目Profile检测逻辑

def _detect_cpp_profile(self, model):
    """检测C++项目特征"""
    confidence = 0.0
    signals = []
    tags = []
    
    # 检测竞赛编程特征
    if self._is_competitive_programming(model):
        confidence += 0.4
        tags.extend(['domain:competitive-programming', 'purpose:icpc'])
        signals.append('competitive-coding')
    
    # 分析头文件依赖模式
    header_patterns = self._analyze_header_includes(model)
    if header_patterns.get('uses_std_headers'):
        confidence += 0.2
        signals.append('std-headers')
    
    # 检测算法题目特征
    if self._has_leetcode_patterns(model):
        confidence += 0.25
        tags.extend(['pattern:leetcode', 'difficulty:mixed'])
    
    # 检测模块组织方式
    if self._has_cpp_module_organization(model):
        confidence += 0.15
        signals.append('module-organized')
    
    return {
        'profile': 'cpp-competitive',
        'confidence': min(confidence, 1.0),
        'signals': signals,
        'tags': tags
    }


4. 具体特征检测方法

def _is_competitive_programming(self, model):
    """检测竞赛编程特征"""
    icpc_indicators = any('icpc' in u.file_path for u in model.units)
    problem_indicators = any(u.role == 'lib' and 'main' in u.symbols for u in model.units)
    return icpc_indicators and problem_indicators

def _has_rust_module_structure(self, model):
    """检测Rust模块结构特征"""
    mod_files = any(u.file_path.endswith('mod.rs') for u in model.units)
    lib_main_combo = any(u.file_path.endswith('lib.rs') for u in model.units) and \
                    any(u.file_path.endswith('main.rs') for u in model.units)
    return mod_files or lib_main_combo

def _analyze_header_includes(self, model):
    """分析C++头文件包含模式"""
    results = {
        'uses_std_headers': False,
        'uses_bits_stdc': False,
        'common_headers': set()
    }
    
    for dep in model.dependency_pool:
        if 'include' in dep.target:
            if 'bits/stdc++.h' in dep.target:
                results['uses_bits_stdc'] = True
            elif any(std_header in dep.target for std_header in ['iostream', 'vector', 'algorithm']):
                results['uses_std_headers'] = True
                
    return results


5. 更新PIRBuilder中的Profile渲染

确保PIRBuilder正确渲染新的profile信息：
def _generate_accurate_profiles(self):
    """生成准确的profile信息"""
    profiles = {}
    
    # 语言主导型profile
    main_profile = self.canonicalizer.detect_language_profile(self.model)
    profiles[main_profile['profile']] = {
        'confidence': main_profile['confidence'],
        'tags': main_profile['tags'],
        'signals': main_profile['signals']
    }
    
    # 设置active profile
    self.model.active_profile = main_profile['profile']
    self.model.profiles = profiles
    
    return self._format_profiles_xml()


📊 预期修复结果

修复后，您的PIR文件应该显示这样的准确profile：

Rust项目预期输出：

<profiles>
  active: rust-learning
  rust-learning:
    confidence: 0.85
    tags:
      - ecosystem:cargo
      - build:rustc
      - purpose:learning
      - domain:algorithms
    signals:
      - cargo-project
      - mod-structure
      - rust-stdlib
</profiles>


C++项目预期输出：

<profiles>
  active: cpp-competitive
  cpp-competitive:
    confidence: 0.80
    tags:
      - domain:competitive-programming
      - purpose:icpc
      - pattern:leetcode
      - difficulty:mixed
    signals:
      - competitive-coding
      - std-headers
      - module-organized
</profiles>


🚀 实施步骤

1. 立即修复：更新ProfileCanonicalizer中的语言检测逻辑
2. 测试验证：对两个项目重新运行PIR生成，检查profile准确性
3. 特征优化：根据实际项目特征调整检测算法的权重
4. 置信度校准：确保置信度真实反映推断的可靠性

这个解决方案将显著提升profile推断的准确性，让PIR文件真正反映项目的技术特征。您需要重点修改core/profile_canon.py中的检测逻辑，特别是加强语言特定特征的识别能力。