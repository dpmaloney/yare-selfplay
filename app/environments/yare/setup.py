from setuptools import setup, find_packages

setup(
    name='yare',
    version='0.1.0',
    description='Yare Gym Environment',
    packages=find_packages(),
    install_requires=[
        'gym>=0.9.4',
        'numpy>=1.13.0',
    ]
)


