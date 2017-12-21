import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'bcrypt',
    'blinker',
    'mongoengine',
    'nose2',
    'cov-core',
    'marshmallow',
    'webtest',
    'waitress'
]

setup(
    name='stackcite.users',
    version='0.0',
    description='A micro-service managing users and authenticaiton.',
    long_description=README + '\n\n' + CHANGES,
    author='Konrad R.K. Ludwig',
    author_email='konrad.rk.ludwig@gmail.com',
    url='http://www.konradrkludwig.com/',
    packages=['stackcite.users'],
    namespace_packages=['stackcite'],
    install_requires=requires,
    classifiers=[
    "Programming Language :: Python",
    "Framework :: Pyramid",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    keywords='web pyramid pylons',
    include_package_data=True,
    zip_safe=False,
    entry_points="""\
    [paste.app_factory]
    main = stackcite.users:main
    """,
)
