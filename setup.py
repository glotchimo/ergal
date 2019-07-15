import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ergal",
    version="1.1.2",
    author="Elliott Maguire",
    author_email="me@elliott-m.com",
    description="A versatile tool for cleaner integrations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/symvo/ergal",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
