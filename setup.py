#!/usr/bin/env python3
"""
iOS Traffic Intelligence
从 iOS 应用流量（HAR/mitmproxy）中提取 API 端点、检测 IDOR/BOLA 模式，
输出给 Nuclei 扫描器和 Rota 代理池。
"""
from setuptools import setup, find_packages

setup(
    name="ios-traffic-intel",
    version="0.1.0",
    description="iOS app traffic analyzer for bug bounty & mobile security testing",
    author="sssppp-cooled",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "black>=22.0", "mypy>=0.990"],
    },
    entry_points={
        "console_scripts": [
            "ios-traffic=ios_traffic_intel.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
