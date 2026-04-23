from setuptools import setup, find_packages

setup(
    name="pirgen",
    version="0.6.0",
    description="AIR - AI-friendly Project Intermediate Representation (Token-optimized)",
    author="daivy",
    author_email="2259492701@qq.com",
    url="https://github.com/daivy/air",
    license="MIT",
    keywords=["PIR", "code-analysis", "intermediate-representation"],
    packages=find_packages(include=["pirgen", "pirgen.*"]),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.0", "black>=23.0", "isort>=5.12"],
    },
    entry_points={
        "console_scripts": [
            "air=pirgen.pirgen:main",
        ]
    },
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
    ],
)
