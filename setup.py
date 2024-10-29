# Create setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gallbladder-analysis",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive gallbladder surgery analysis toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gallbladder_analysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gallbladder-scrape=gallbladder_analysis.cli:scrape",
            "gallbladder-process=gallbladder_analysis.cli:process",
            "gallbladder-analyze=gallbladder_analysis.cli:analyze",
            "gallbladder-dashboard=gallbladder_analysis.cli:dashboard",
        ],
    },
    include_package_data=True,
)