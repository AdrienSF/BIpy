from setuptools import find_packages, setup

setup(
    name='BIpy',
    packages=find_packages(include=['BIpy']),
    version='0.1.0',
    description='py for BI',
    author='Self',
    license='BSD 3-Clause License',
    install_requires=['numpy==1.20.3', 'pylsl==1.14.0'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)