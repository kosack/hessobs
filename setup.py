from setuptools import setup

import sys
if sys.version_info < (3,0):
    sys.exit('Sorry, Python < 3.0 is not supported')

setup(name='hessobs',
      version='0.1',
      description='Observation Scheduleing and exploration for HESS',
      url='',
      author='Karl Kosack',
      author_email='karl.kosack@cea.fr',
      license='BSD',
      packages=['hessobs'],
      install_requires=[
          'astropy',
          'pymysql',
          'ephem',
          'pandas'
      ],
      scripts=[
          'bin/hessobs-animate',
          'bin/hessobs-ingestproposal',
          'bin/hessobs-summary',
          'bin/hessobs-verifyprop',
          'bin/hessobs-visplot'
      ],
      zip_safe=False)
