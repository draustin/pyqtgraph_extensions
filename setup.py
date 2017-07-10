from setuptools import setup, find_packages

setup(name="pyqtgraph_extensions",
      version=0.1,
      description="Extensions for pyqtgraph",
      long_description="""pyqtgraph_extensions many add-ons for pyqtgraph.""",
      author='Dane Austin',
      author_email='dane_austin@fastmail.com.au',
      url='https://bitbucket.org/draustin/pyqtgraph_extensions',
      license='BSD',
      packages=find_packages(),#['pyqtgraph_extensions', 'pyqtgraph_extended'],
      install_requires=['pyqtgraph'],
      package_data={'pyqtgraph_extensions':['*.png']}
)
