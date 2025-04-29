from setuptools import setup, find_packages

setup(
    name="financial-minions",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "openai>=1.0.0",
        "anthropic>=0.5.0",
        "pytest>=7.0.0",
        "asyncio>=3.4.3",
        "aiohttp>=3.8.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A multi-agent orchestration system for financial analysis tasks",
) 