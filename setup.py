from setuptools import setup

setup(
    name='budget',
    version='1.2.0',
    packages=['budget'],
    entry_points={
        'console_scripts': [
            'budget=budget.__main__:main'
        ]
    })
