"""Defines setuptools metadata."""

import setuptools

setuptools.setup(
    name="chemMAP",
    packages=setuptools.find_packages(),
    install_requires=[
        "rdflib",
        "requests",
        "pandas",
        "scikit-learn"
    ],
    python_requires=">=3.7",
)