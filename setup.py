from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='VSX',
      version=version,
      description="Storage management",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Marco De Benedetto',
      author_email='debe@galliera.it',
      url='http://git.galliera.it/debe/vsx.git',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
