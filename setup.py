from setuptools import setup, find_packages

with open("./README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="vaspvis",
    version="1.4.3",
    description="A highly flexible and customizable library for visualizing electronic structure data from VASP calculations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.9",
    install_requires=[
        "scipy",
        "pymatgen",
        "matplotlib",
        "numpy",
        "pandas",
        "ase",
        "fastdtw",
        "scikit-learn",
    ],
    url="https://github.com/caizefeng/vaspvis",
    author="Derek Dardzinski",
    maintainer='Zefeng Cai',
    license="MIT",
)
