from setuptools import setup, find_packages

setup(
    name="timeseries-preproc",
    version="0.1.0",
    description="Preprocessing pipeline for multiple univariate time series (smoothing, arc normalization, peak annotation).",
    author="Monish",
    author_email="monish2work@gmail.com",
    url="",
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.20",
        "pandas>=1.3",
        "fastapi",
        "uvicorn[standard]",
        "pydantic"

    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
        ],
    },
)