#!/usr/bin/env python
import os
import sys
from setuptools import setup

# Prepare and send a new release to PyPI
if "release" in sys.argv[-1]:
    os.system("python setup.py sdist")
    os.system("python setup.py bdist_wheel")
    os.system("twine upload dist/*")
    os.system("rm -rf dist/telraam_data*")
    sys.exit()

# Load the __version__ variable without importing the package already
exec(open('telraam_data/version.py').read())

# DEPENDENCIES
# 1. What are the required dependencies?
with open('requirements.txt') as f:
    install_requires = f.read().splitlines()
# 2. What dependencies required to run the unit tests?
tests_require = ['pytest']


setup(name='telraam_data',
      version=__version__,
      description="A friendly package to download traffic count data from the Telraam API.",
      long_description=open('README.rst').read(),
      author='Geert Barentsen',
      author_email='geert@barentsen.be',
      url='https://www.geert.io',
      license='MIT',
      package_dir={'telraam_data': 'telraam_data'},
      packages=['telraam_data'],
      install_requires=install_requires,
      setup_requires=['pytest-runner'],
      tests_require=tests_require,
      include_package_data=True,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Intended Audience :: Science/Research",
          ],
      )
