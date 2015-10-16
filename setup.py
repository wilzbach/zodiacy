#!/usr/bin/env python3

from setuptools import setup
from os import path
from setuptools.command.install import install
import os

here = path.abspath(path.dirname(__file__))
readme = path.join(here, 'README.md')


def is_heroku():
    return int(os.environ.get("PORT", -1)) > 0


def check_nltk(entries):
    """ checks whether required nltk parts are available """
    import nltk
    for entry in entries:
        try:
            nltk.data.find(entry[0])
        except LookupError:
            print("downloading %s", entry[1])
            nltk.download(entry[1])


class CustomInstall(install):

    def run(self):
        install.run(self)
        if not is_heroku():
            check_nltk([('corpora/wordnet', 'wordnet'),
                        ('tokenizers/punkt/english.pickle', 'punkt')])

try:
    import pypandoc
    long_description = pypandoc.convert(readme, 'rst')
except (IOError, ImportError):
    with open(readme, encoding='utf-8') as f:
        long_description = f.read()

setup(name='zodiacy',
      version='1.0',
      description='Horoscope generation',
      long_description=long_description,
      author='Project Zodiacy',
      author_email='greenify+zodiacy@gmail.com',
      license='MIT',
      url='https://github.com/greenify/zodiacy',
      package_dir={'zodiacy': 'src'},
      packages=['zodiacy'],
      package_data={'zodiacy': ['data/zodiac.sqlite']},
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Religion',
          'Natural Language :: English',
          'Topic :: Scientific/Engineering :: Astronomy',
          'Topic :: Scientific/Engineering :: Artificial Intelligence',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
      ],
      keywords='horoscope astronomy zodiac star signs',
      install_requires=['nltk>3', 'wordnik-py3>2.1',
                        'astral>0.8', 'SQLAlchemy>1'],
      entry_points={
          'console_scripts': [
              'zodiacy=zodiacy.cli:main',
          ],
      },
      cmdclass=dict(install=CustomInstall)
      )
