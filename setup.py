from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="pyqtgraph_extensions",
    description="Extensions for pyqtgraph",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Dane Austin',
    author_email='dane_austin@fastmail.com.au',
    url='https://github.com/draustin/pyqtgraph_extensions',
    packages=find_packages(),#['pyqtgraph_extensions', 'pyqtgraph_extended'],
    install_requires=['pyqtgraph', 'scipy'],
    # Need to include GUI PNGs. See https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files and
    # https://github.com/pypa/setuptools_scm#file-finders-hook-makes-most-of-manifestin-unnecessary.
    include_package_data=True,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"]
)
