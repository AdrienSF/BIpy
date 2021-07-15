from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='BIpy',
    packages=find_packages(include=['BIpy', 'BIpy.bci']),
    version='0.2.4',
    description='py for BI',
    author='Self',
    license='BSD 3-Clause License',
    install_requires=['numpy==1.20.3', 'pylsl==1.13.6', 'psychopy==2021.2.0', 'mne==0.23.0', 'pyxdf==1.16.3', 'scikit-learn==0.24.2'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
    long_description=long_description,
    long_description_content_type="text/markdown"
)