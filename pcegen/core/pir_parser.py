"""
PIR Parser - 解析 PIR 文件
"""
import re
from typing import Dict, List, Optional


class PIRParser:
    """PIR 文件解析器"""

    def __init__(self):
        self.patterns = {
            'meta': re.compile(r'<meta>(.*?)</meta>', re.DOTALL),
            'units': re.compile(r'<units>(.*?)</units>', re.DOTALL),
            'dependency_pool': re.compile(r'<dependency-pool>(.*?)</dependency-pool>', re.DOTALL),
            'dependencies': re.compile(r'<dependencies>(.*?)</dependencies>', re.DOTALL),
            'symbols': re.compile(r'<symbols>(.*?)</symbols>', re.DOTALL),
            'profiles': re.compile(r'<profiles>(.*?)</profiles>', re.DOTALL),
            'layout': re.compile(r'<layout>(.*?)</layout>', re.DOTALL),
            'code_snippets': re.compile(r'<code-snippets>(.*?)</code-snippets>', re.DOTALL),
        }

    def parse(self, pir_text: str) -> Dict:
        """
        解析 PIR 文本

        Args:
            pir_text: PIR 文本内容

        Returns:
            PIR 数据字典
        """
        pir_data = {
            'meta': {},
            'units': [],
            'dependency_pool': [],
            'dependencies': {},
            'symbols': [],
            'profiles': {},
            'layout': {},
            'snippets': []
        }

        # 解析 meta
        meta_match = self.patterns['meta'].search(pir_text)
        if meta_match:
            pir_data['meta'] = self._parse_meta(meta_match.group(1))

        # 解析 units
        units_match = self.patterns['units'].search(pir_text)
        if units_match:
            pir_data['units'] = self._parse_units(units_match.group(1))

        # 解析 symbols
        symbols_match = self.patterns['symbols'].search(pir_text)
        if symbols_match:
            pir_data['symbols'] = self._parse_symbols(symbols_match.group(1), pir_data['units'])

        # 解析 dependency pool
        dep_pool_match = self.patterns['dependency_pool'].search(pir_text)
        if dep_pool_match:
            pir_data['dependency_pool'] = self._parse_dependency_pool(dep_pool_match.group(1))

        # 解析 dependencies
        deps_match = self.patterns['dependencies'].search(pir_text)
        if deps_match:
            pir_data['dependencies'] = self._parse_dependencies(deps_match.group(1))

        # 解析 profiles
        profiles_match = self.patterns['profiles'].search(pir_text)
        if profiles_match:
            pir_data['profiles'] = self._parse_profiles(profiles_match.group(1))

        # 解析 layout
        layout_match = self.patterns['layout'].search(pir_text)
        if layout_match:
            pir_data['layout'] = self._parse_layout(layout_match.group(1))

        # 解析 snippets
        snippets_match = self.patterns['code_snippets'].search(pir_text)
        if snippets_match:
            pir_data['snippets'] = self._parse_snippets(snippets_match.group(1))

        return pir_data

    def _parse_meta(self, meta_text: str) -> Dict:
        """解析 meta 部分"""
        meta = {}
        lines = meta_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                meta[key.strip()] = value.strip()
        return meta

    def _parse_units(self, units_text: str) -> List[Dict]:
        """解析 units 部分"""
        units = []
        lines = units_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                # 格式: u0: __init__.py type=PY role=lib module=pirgen
                parts = line.split(':', 1)
                uid = parts[0].strip()
                rest = parts[1].strip()

                # 解析属性
                attrs = {}
                for attr in rest.split():
                    if '=' in attr:
                        key, value = attr.split('=', 1)
                        attrs[key] = value

                unit = {
                    'id': uid,
                    'path': attrs.get('', rest.split()[0] if rest.split() else ''),
                    'type': attrs.get('type', ''),
                    'role': attrs.get('role', ''),
                    'module': attrs.get('module', ''),
                    'symbols': []  # 添加symbols列表
                }

                # 提取路径（第一个不是属性的部分）
                path_match = re.match(r'^([^\s=]+)', rest)
                if path_match:
                    unit['path'] = path_match.group(1)

                units.append(unit)
        return units

    def _parse_dependency_pool(self, pool_text: str) -> List[Dict]:
        """解析 dependency pool 部分"""
        pool = []
        lines = pool_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                # 格式: d0: import:[analyzers.base]
                parts = line.split(':', 2)
                if len(parts) == 3:
                    dep = {
                        'id': parts[0].strip(),
                        'verb': parts[1].strip(),
                        'target': parts[2].strip()
                    }
                    pool.append(dep)
        return pool

    def _parse_dependencies(self, deps_text: str) -> Dict[str, List[str]]:
        """解析 dependencies 部分"""
        deps = {}
        lines = deps_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and '->refs:' in line:
                # 格式: u1->refs:[d3 d1 d4 d6 d10 d5 d2]
                match = re.match(r'(\w+)->refs:\[(.*?)\]', line)
                if match:
                    uid = match.group(1)
                    refs = match.group(2).split()
                    deps[uid] = refs
        return deps

    def _parse_symbols(self, symbols_text: str, units: List[Dict]) -> List[Dict]:
        """解析 symbols 部分"""
        symbols = []
        lines = symbols_text.strip().split('\n')

        # 创建unit_id到unit的映射
        unit_map = {unit['id']: unit for unit in units}

        for line in lines:
            line = line.strip()
            if line and ':' in line:
                # 格式: load_source_code:u1 func
                # 或: load_source_code:u1 func entry=true
                parts = line.split(':', 1)
                name = parts[0].strip()
                rest = parts[1].strip()

                # 解析
                attrs = {}
                kind = ''
                unit_id = ''

                # 第一个词应该是 unit_id
                if rest:
                    parts2 = rest.split()
                    if parts2:
                        unit_id = parts2[0]  # 第一个是unit_id
                        # 第二个词是 kind
                        if len(parts2) > 1:
                            kind = parts2[1]
                        # 解析属性
                        for attr in parts2[2:]:
                            if '=' in attr:
                                key, value = attr.split('=', 1)
                                attrs[key] = value

                symbol = {
                    'name': name,
                    'kind': kind,
                    'attrs': attrs
                }

                # 将symbol添加到对应的unit中
                if unit_id and unit_id in unit_map:
                    unit_map[unit_id]['symbols'].append(symbol)

                symbols.append(symbol)
        return symbols

    def _parse_profiles(self, profiles_text: str) -> Dict:
        """解析 profiles 部分"""
        profiles = {}
        lines = profiles_text.strip().split('\n')
        current_profile = None

        for line in lines:
            line = line.strip()

            # 检查是否是 profile 定义
            profile_match = re.match(r'^\s*(\w+):', line)
            if profile_match and not line.startswith('  '):
                current_profile = profile_match.group(1)
                profiles[current_profile] = {'tags': [], 'signals': []}
                continue

            # 检查是否是 active profile
            active_match = re.match(r'^\s*active:\s*(\w+)', line)
            if active_match:
                profiles['active'] = active_match.group(1)
                continue

            # 解析 profile 内容
            if current_profile:
                # confidence
                conf_match = re.match(r'^\s*confidence:\s*([\d.]+)', line)
                if conf_match:
                    profiles[current_profile]['confidence'] = float(conf_match.group(1))
                    continue

                # tags
                tag_match = re.match(r'^\s*-\s*(.+)', line)
                if tag_match:
                    # 判断是 tag 还是 signal
                    if 'tags:' in profiles_text[:profiles_text.index(line)]:
                        profiles[current_profile]['tags'].append(tag_match.group(1))
                    else:
                        profiles[current_profile]['signals'].append(tag_match.group(1))

        return profiles

    def _parse_layout(self, layout_text: str) -> Dict:
        """解析 layout 部分"""
        layout = {}
        lines = layout_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                layout[key.strip()] = value.strip()
        return layout

    def _parse_snippets(self, snippets_text: str) -> List[Dict]:
        """解析 code snippets 部分"""
        snippets = []
        # 使用正则表达式匹配 snippet
        pattern = re.compile(r'<snippet\s+unit="([^"]+)">.*?<!\[CDATA\[(.*?)\]\]>.*?</snippet>', re.DOTALL)
        matches = pattern.findall(snippets_text)
        for uid, content in matches:
            snippets.append({
                'unit': uid,
                'content': content.strip()
            })
        return snippets
