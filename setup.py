from setuptools import setup, find_packages

setup(
    name="thermodynamic-substrate",
    version="1.0.1",
    description="Non-von Neumann runtime with thermodynamic execution physics",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="TCS Contributors",
    author_email="",
    url="https://github.com/prettybusysolutions-eng/thermodynamic-substrate",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.20.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai runtime thermodynamics agents autonomous",
)
