import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="orchestra",
    version="0.0.9",
    author="Christoph Berger",
    author_email="c.berger@tum.de",
    description="Bulk segmentation for the BraTS challenge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/christophantonberger/orchestra",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
