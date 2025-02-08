from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='apb5vip',
    version='0.1.0',  # Start with a version number
    author="Gergo Gacs",
    author_email="gacsgergo@gmail.com",
    description="An AMBA APB5 VIP using pyuvm and cocotb",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires=">=3.13",
    install_requires=[
        "cocotb>=1.6.0,<2.0",
        "pyuvm",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.13",
        "Topic :: Hardware :: Verification",
        "Framework :: cocotb :: UVM",
    ],
    keywords="amba, apb5, vip, verification, cocotb, pyuvm",
)
