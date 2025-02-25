from setuptools import setup, find_packages

setup(
    name="adaptive_mcp_server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.2.1",
        "pytest-asyncio>=0.20.3",
        "pytest-cov>=4.0.0",
    ],
)
