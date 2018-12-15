from setuptools import setup

setup(
    name='budget',
    version='0.1.0',
    packages=['budget'],
    entry_points={
        'console_scripts': [
            'budget=budget.__main__:main'
        ]
    })
