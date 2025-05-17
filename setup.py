from setuptools import setup, find_packages

setup(
    name="python-project",
    version="0.1.0",
    description="A basic Python project template",
    author="Praveen Andra",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
