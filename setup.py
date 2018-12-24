from setuptools import setup, find_packages

setup(name="pyqtgraph_extensions",
      version=0.2,
      description="Extensions for pyqtgraph",
      long_description="""pyqtgraph_extensions many add-ons for pyqtgraph.""",
      author='Dane Austin',
      author_email='dane_austin@fastmail.com.au',
      url='https://bitbucket.org/draustin/pyqtgraph_extensions',
      license='BSD',
      packages=find_packages(),#['pyqtgraph_extensions', 'pyqtgraph_extended'],
      install_requires=['pyqtgraph', 'pyqt5', 'pytest', 'pytest-qt', 'scipy', 'mathx'],
      package_data={'pyqtgraph_extensions':['*.png']},
      # This is needed to make it read MANIFEST.IN. Discovering this was a giant
      # pain. See
      # https://svn.python.org/projects/sandbox/trunk/setuptools/setuptools.txt
      include_package_data=True,
      dependency_links=['https://github.com/draustin/mathx/tarball/master#egg=mathx-0.1']
)
