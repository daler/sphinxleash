import os
from setuptools import setup, find_packages

long_description = """
Lightweight framework for programatically generating Sphinx docs.
"""

version = open('sphinxleash/version.py')\
    .readline()\
    .split("=")[-1]\
    .strip()\
    .replace('"', '')

setup(
        name="sphinxleash",
        author="Ryan Dale",
        version=version,
        install_requires=['sphinx', 'six'],
        description='Lightweight framework for generating Sphinx docs',
        long_description=long_description,
        url="none",
        author_email="dalerr@niddk.nih.gov",
        packages=find_packages(),
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            ]
    )
