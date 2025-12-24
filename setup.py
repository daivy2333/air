from setuptools import setup, find_packages
import os

# 读取 README 文件作为长描述
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name="air-tool",
    version="0.1.0",
    description="AIR - Application Interface Center for PIR forward and reverse engineering",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="daivy",
    author_email="2259492701@qq.com",
    url="https://github.com/daivy/air",
    license="MIT",
    keywords=["PIR", "reverse-engineering", "code-analysis", "project-reconstruction"],

    # 包的配置
    packages=find_packages(
        include=["air", "air.*", "pirgen", "pirgen.*", "pir_reconstructor", "pir_reconstructor.*"],
        exclude=["tests*", "docs*", "md*", "spec*", "初版*", "re*", "ir规范*", "talk*", "services*"]
    ),
    # 包含数据文件
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.toml", "*.yaml", "*.yml"],
    },

    # Python 版本要求
    python_requires=">=3.9",

    # 依赖
    install_requires=[],

    # 开发依赖 (可选，通常放在 requirements-dev.txt)
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "isort>=5.12",
        ]
    },

    # 命令行入口
    entry_points={
        "console_scripts": [
            "air=air.app:main",
        ]
    },

    # 分类器
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Reverse Engineering",
    ],
)
