#!/usr/bin/env python
from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='stack_exchange_graph_data',
    version='0.0.1',
    license='MIT',
    description='Converts Stack Exchange data dumps to Gephi importable '
                'spreadsheets.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Peilonrayz',
    author_email='peilonrayz@gmail.com',
    url='https://example.com/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    keywords='stackexchange sede',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'docutils',
        'recommonmark',
        'sphinx',
        'beautifulsoup4',
        'defusedxml',
        'requests',
        'pylzma',
    ],
    extras_require={
        'dev':  [
            'tox',
            'docutils-stubs',
        ]
    },
    entry_points={
        "console_scripts": [
            "segd=stack_exchange_graph_data.__main__:main"
        ]
    },
)
