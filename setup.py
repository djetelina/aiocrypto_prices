from setuptools import setup, find_packages
# noinspection PyPep8Naming
from setuptools import Command
from codecs import open
import os
import sys

if sys.version_info.major < 3:
    sys.exit('Python 2 is not supported')
elif sys.version_info.minor < 6:
    sys.exit('Python 3.6+ required')


requirements = ['aiohttp>=2.3.9']

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(name='aiocrypto_prices',
      version='0.0.2.1',
      description='asyncio cryptocurrency prices library',
      long_description=long_description,
      url='',
      author='David Jetelina',
      author_email='david@djetelina.cz',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='cryptocurrency finance crypto bitcoin asyncio',
      packages=find_packages(),
      install_requires=requirements
      )
