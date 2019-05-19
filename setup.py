from setuptools import setup, find_packages

def get_github_url(package_name: str, user_name: str):
    """URL for one of my GitHub repos for install_requires.

    See PEP 508.
    """
    # Will keep ssh version for reference.
    # '%s @ git+ssh://git@github.com/draustin/%s.git'%(name, name)
    return '%s @ git+https://github.com/%s/%s.git'%(package_name, user_name, package_name)

setup(name="pyqtgraph_extensions",
      version=0.2,
      description="Extensions for pyqtgraph",
      long_description="""pyqtgraph_extensions many add-ons for pyqtgraph.""",
      author='Dane Austin',
      author_email='dane_austin@fastmail.com.au',
      url='https://github.com/draustin/pyqtgraph_extensions',
      license='BSD',
      packages=find_packages(),#['pyqtgraph_extensions', 'pyqtgraph_extended'],
      install_requires=[get_github_url('pyqtgraph', 'pyqtgraph'), 'PyQt5', 'pytest', 'pytest-qt', 'scipy',
                        get_github_url('mathx', 'draustin'), 'PyOpenGL'],
      package_data={'pyqtgraph_extensions':['*.png']},
      # This is needed to make it read MANIFEST.IN. Discovering this was a giant
      # pain. See
      # https://svn.python.org/projects/sandbox/trunk/setuptools/setuptools.txt
      include_package_data=True,
      dependency_links=['https://github.com/draustin/mathx/tarball/master#egg=mathx-0.1']
)
