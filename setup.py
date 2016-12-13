from setuptools import setup

setup(
    name='licecomb',
    description='Check GitHub repositories for license files',
    author='Kristian Glass',
    author_email='licecomb@doismellburning.co.uk',
    url='https://github.com/doismellburning/licecomb',
    version='0.1',
    license='mit',
    install_requires=[
        "PyGithub",
        "requests >=1.2, <1.3",
    ],
    packages=['licecomb'],
    entry_points={
        "console_scripts": [
            "licecomb = licecomb:main",
        ],
    },
)
