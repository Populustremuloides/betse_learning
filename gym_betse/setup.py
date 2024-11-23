# gym_betse/setup.py

from setuptools import setup, find_packages

setup(
    name='gym_betse',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'gymnasium',
        'numpy',
        'h5py',
        'torch',
        # Add other dependencies
    ],
    description='Gymnasium environment for BETSE simulations',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/gym_betse',
)
