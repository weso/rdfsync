from setuptools import setup
from os import path

curr_dir = path.abspath(path.dirname(__file__))
with open(path.join(curr_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='rdfsync',
    version='0.0.1',
    packages=['rdfsync', 'rdfsync.util', 'rdfsync.githubcon', 'rdfsync.wb2rdf'],
    url='https://github.com/weso/rdfsync',
    license='MIT',
    author='Othmane Bakhtaoui',
    author_email='uo259323@uniovi.es',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'requests==2.23.0', 'rdflib==5.0.0', 'PyGithub==1.53'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7'
    ]
)
