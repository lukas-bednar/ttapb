from setuptools import setup, find_packages

import os
description = 'Simple converter of template to apb'
long_description = description
if os.path.exists('README.rst'):
    long_description = open('README.rst').read()

setup(
    name='ttapb',
    version='0.2',
    include_package_data=True,
    packages=find_packages(),
    description=description,
    long_description=long_description,
    url='http://github.com/karmab/ttapb',
    author='Karim Boumedhel',
    author_email='karimboumedhel@gmail.com',
    license='ASL',
    install_requires=[
        'PyYAML',
    ],
    entry_points='''
        [console_scripts]
        ttapb=ttapb.cli:cli
    ''',
)
