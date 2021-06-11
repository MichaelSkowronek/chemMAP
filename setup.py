"""Defines setuptools metadata."""

import setuptools

setuptools.setup(
    name="chemMAP",
    packages=setuptools.find_packages(),
    install_requires=[
        "rdflib",
        "requests",
        "pandas",
        "scikit-learn",
        "numpy"
    ],
    python_requires=">=3.7",
)
