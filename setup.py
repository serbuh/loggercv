from setuptools import setup, find_packages

setup(
    name='loggercv',
    version='1.0.0',
    packages=find_packages(exclude=['tests']),
    author='sergeybu',
    description='Logger with handlers',
)
