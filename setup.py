from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="scoreboard",
    version="1.0.0",
    author="Alejandro Olguin",
    author_email="your.email@example.com",
    description="Sistema de puntuación automatizado para competencias de robótica usando visión por computadora",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlejandroOlguin-am/scoreboard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "scoreboard=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/calibration/*.yaml", "assets/sounds/*"],
    },
)
