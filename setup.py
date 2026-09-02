from setuptools import setup, find_packages

setup(
    name="connectome-core",
    version="1.0.0",
    description="Structural Connectome Core Extraction Pipeline across Multi-Resolution Cortical and Subcortical Atlases",
    author="Abolfazl (Reza) Alipour",
    url="https://github.com/Abolfazl-Alipour/connectome-core",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.22.0",
        "scipy>=1.8.0",
        "networkx>=2.8.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "nibabel>=4.0.0",
        "pandas>=1.4.0",
        "tqdm>=4.64.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
    ],
)
