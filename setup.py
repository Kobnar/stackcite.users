import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

requires = [
    'flask',
    'bcrypt',
    'blinker',
    'mongoengine',
    'nose2',
    'cov-core'
]

setup(
    name='stackcite.users',
    version='0.0',
    description='A micro-service managing users and authenticaiton.',
    long_description=README + '\n\n' + CHANGES,
    author='Konrad R.K. Ludwig',
    author_email='konrad.rk.ludwig@gmail.com',
    url='http://www.konradrkludwig.com/',
    packages=find_packages(),
    namespace_packages=['stackcite'],
    install_requires=requires
)
