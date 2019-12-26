from setuptools import setup, find_packages

def get_github_url(package_name, user_name):
    """URL for one of my GitHub repos for install_requires.

    See PEP 508.
    """
    # Will keep ssh version for reference.
    # '%s @ git+ssh://git@github.com/draustin/%s.git'%(name, name)
    return '%s @ git+https://github.com/%s/%s.git'%(package_name, user_name, package_name)

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
    install_requires=[get_github_url('pyqtgraph', 'pyqtgraph'),  get_github_url('mathx', 'draustin')],
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
