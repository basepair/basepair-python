'''basepair package'''
import re
from setuptools import setup

with open('basepair/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.md') as file:
    long_description = file.read()

packages = [
    'basepair',
    'basepair.helpers',
    'basepair.infra',
    'basepair.infra.configuration',
    'basepair.infra.webapp',
    'basepair.utils',
]

setup(
    name='basepair',
    packages=packages,
    version=version,
    description="Python client for Basepair's API",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Basepair',
    author_email='info@basepairtech.com',
    url='https://bitbucket.org/basepair/basepair',
    download_url='https://bitbucket.org/basepair/basepair/get/{}.tar.gz'
    .format(version),
    keywords=[
        'bioinformatics',
        'ngs analysis',
        'dna-seq',
        'rna-seq',
        'chip-seq',
        'atac-seq'
    ],
    install_requires=[
        'boto3',
        'future',
        'requests',
        'awscli',
        'tabulate',
    ],
    scripts=['bin/basepair'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'License :: Free for non-commercial use',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ]
)
