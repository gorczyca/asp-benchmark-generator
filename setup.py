from setuptools import setup

setup(
    name='asp-benchmark-generator',
    version=0.1,
    description='GUI tool for benchmark generation for configuration problem in ASP.',
    author='Piotr Gorczyca',
    author_email='gorczycapj@gmail.com',
    install_requires=[
        'pypubsub>=4.0.3',
        'clingo>=5.4.0'
    ]
)
