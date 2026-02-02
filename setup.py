from setuptools import setup, find_packages

setup(
    name="webcopy",
    version="1.0.0",
    description="Ferramenta para copiar sites e organizar assets localmente",
    author="WebCopy",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.0.0",
        "click>=8.1.0",
        "brotli>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "webcopy=webcopy.cli:main",
        ],
    },
)
