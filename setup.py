import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DaVE-StanfordVLSI", # Replace with your own username
    version="0.0.1",
    author="Stanford VLSI",
    author_email="dstanley@Stanford.edu",
    description="Tools for analog circuit modeling, validation, and generation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StanfordVLSI/DaVE",
    packages=setuptools.find_packages(),
    install_requires = [
        'BitVector',
        'configobj',
        'empy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        # for now, licesnse is very slightly modified BSD
        #'License :: OSI Approved :: BSD 3-clause "New" or "Revised License"',
    ],
    # TODO earlier versions might be fine
    python_requires='>=3.6',
)
