"""
分析器配置文件
定义各语言分析器的能力和特性
"""

# 分析器能力配置
ANALYZER_CAPABILITIES = {
    'python': {
        'views': ['impl', 'api', 'summary', 'type_definition', 'call_graph'],
        'features': ['classes', 'decorators', 'type_hints', 'async', 'dataclass'],
        'parser': 'ast',
        'supports': {
            'fields': True,
            'methods': True,
            'signatures': True,
            'decorators': True,
            'type_hints': True,
            'async': True,
            'callchain': True,
            'behavior': True
        }
    },
    'rust': {
        'views': ['impl', 'summary', 'type_definition'],
        'features': ['structs', 'enums', 'traits', 'generics', 'unsafe', 'async'],
        'parser': 'regex',
        'requires_build': False,
        'supports': {
            'fields': True,
            'methods': True,
            'signatures': True,
            'generics': True,
            'traits': True,
            'unsafe': True,
            'async': True,
            'impl_blocks': True,
            'callchain': True,
            'behavior': True
        }
    },
    'c': {
        'views': ['impl', 'api', 'summary', 'type_definition'],
        'features': ['structs', 'enums', 'pointers', 'unions', 'typedefs'],
        'parser': 'regex',
        'supports': {
            'fields': True,
            'methods': True,
            'signatures': True,
            'pointers': True,
            'enums': True,
            'unions': True,
            'typedefs': True,
            'callchain': True,
            'behavior': True
        }
    },
    'cpp': {
        'views': ['impl', 'api', 'summary', 'type_definition'],
        'features': ['classes', 'templates', 'stl', 'inheritance', 'access_control'],
        'parser': 'regex',
        'supports': {
            'fields': True,
            'methods': True,
            'signatures': True,
            'templates': True,
            'inheritance': True,
            'access_control': True,
            'stl': True,
            'virtual': True,
            'override': True,
            'callchain': True,
            'behavior': True
        }
    },
    'asm': {
        'views': ['impl', 'summary'],
        'features': ['labels', 'instructions', 'sections'],
        'parser': 'regex',
        'supports': {
            'labels': True,
            'instructions': True,
            'sections': True,
            'directives': True
        }
    },
    'ld': {
        'views': ['summary'],
        'features': ['symbols', 'sections', 'memory_layout'],
        'parser': 'regex',
        'supports': {
            'symbols': True,
            'sections': True,
            'memory_layout': True
        }
    }
}

# 视图类型定义
VIEW_TYPES = {
    'impl': {
        'description': '实现视图',
        'extract_method': 'extract_implementation',
        'supports': ['python', 'rust', 'c', 'cpp', 'asm']
    },
    'api': {
        'description': 'API视图',
        'extract_method': 'extract_signature',
        'supports': ['python', 'rust', 'c', 'cpp']
    },
    'summary': {
        'description': '摘要视图',
        'extract_method': 'extract_behavior',
        'supports': ['python', 'rust', 'c', 'cpp', 'asm', 'ld']
    },
    'type_definition': {
        'description': '类型定义视图',
        'extract_method': 'extract_implementation',
        'supports': ['python', 'rust', 'c', 'cpp']
    },
    'call_graph': {
        'description': '调用图视图',
        'extract_method': 'extract_callchain',
        'supports': ['python', 'rust', 'c', 'cpp']
    },
    'asm': {
        'description': '汇编视图',
        'extract_method': 'extract_asm_info',
        'supports': ['asm']
    },
    'memory_layout': {
        'description': '内存布局视图',
        'extract_method': 'extract_layout_info',
        'supports': ['ld']
    }
}

# 分析器优先级（用于选择最合适的分析器）
ANALYZER_PRIORITY = {
    'python': 1,
    'rust': 2,
    'cpp': 3,
    'c': 4,
    'asm': 5,
    'ld': 6
}

def get_analyzer_capabilities(lang: str) -> dict:
    """获取指定语言的分析器能力"""
    return ANALYZER_CAPABILITIES.get(lang, {})

def supports_view(lang: str, view_type: str) -> bool:
    """检查语言是否支持指定视图类型"""
    caps = get_analyzer_capabilities(lang)
    return view_type in caps.get('views', [])

def get_view_description(view_type: str) -> str:
    """获取视图类型的描述"""
    view_info = VIEW_TYPES.get(view_type, {})
    return view_info.get('description', 'Unknown view')

def get_supported_languages(view_type: str) -> list:
    """获取支持指定视图类型的语言列表"""
    view_info = VIEW_TYPES.get(view_type, {})
    return view_info.get('supports', [])
