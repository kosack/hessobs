from setuptools import setup, find_packages

import sys
if sys.version_info < (3,0):
    sys.exit('Sorry, Python < 3.0 is not supported')

setup(name='hessobs',
      version='0.2',
      description='Observation Scheduling and exploration for HESS',
      url='',
      author='Karl Kosack',
      author_email='karl.kosack@cea.fr',
      license='BSD',
      packages=find_packages(),
      install_requires=[
          'astropy',
          'pymysql',
          'ephem',
          'pandas',
          'matplotlib',
          'scipy',
          'colorama',
          'configobj',
          'sqlalchemy'
      ],
      scripts=[
          'bin/hessobs-animate',
          'bin/hessobs-ingestproposal',
          'bin/hessobs-summary',
          'bin/hessobs-verifyprop',
          'bin/hessobs-visplot'
      ],
      zip_safe=False,
      package_data={'hessobs':['test/darkness2017.dat']}
)
