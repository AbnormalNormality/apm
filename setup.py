from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="alia-apm",
    version="0.1.10",
    description="A collection of Python scripts by me, Alia.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Alia Normal",
    author_email="dan.driscoll@aussiebb.com",
    
    url="https://github.com/AbnormalNormality/apm",

    packages=find_packages(),

    license="MIT",

    install_requires=[
        "discord > 2.0",
    ],
    python_requires=">=3.12",
)
