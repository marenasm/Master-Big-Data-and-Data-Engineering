"""
Script de instalacion del paquete traficFines.
Ejecutar con: python setup.py install
"""

from setuptools import setup, find_packages

setup(
    name="traficFines",
    version="1.0.0",
    description="Descarga, limpieza y analisis de multas de trafico del Ayuntamiento de Madrid.",
    author="Master Big Data & Data Engineering",
    python_requires=">=3.11",
    packages=find_packages(exclude=["tests*", "notebooks*"]),
    install_requires=[
        "pandas>=2.0",
        "requests>=2.28",
        "beautifulsoup4>=4.12",
        "matplotlib>=3.7",
        "numpy>=1.24",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4",
            "pytest-cov>=4.1",
        ]
    },
)