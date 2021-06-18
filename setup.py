from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='BIpy',
    packages=find_packages(include=['BIpy']),
    version='0.1.1',
    description='py for BI',
    author='Self',
    license='BSD 3-Clause License',
    install_requires=['numpy==1.20.3', 'pylsl==1.14.0'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
    long_description=long_description,
    long_description_content_type="text/markdown"
)