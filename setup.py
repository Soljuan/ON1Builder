#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="on1builder",
    version="1.0.0",
    description="ON1Builder - Multi-Chain Trading Bot",
    author="ON1Builder Team",
    author_email="info@on1builder.com",
    url="https://github.com/John0n1/ON1Builder",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "web3>=6.0.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
        "pyyaml>=6.0",
        "hvac>=1.0.0",  # HashiCorp Vault client
        "prometheus-client>=0.12.0",
    ],
    entry_points={
        "console_scripts": [
            "on1builder=python.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.9",
)
