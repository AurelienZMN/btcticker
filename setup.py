import sys
from setuptools import setup
setup(
    name='btcticker-epaper',
    description='BTC ticker e-Paper',
    author='AurelienZMN',
    package_dir={'': 'lib'},
    packages=['waveshare_epd'],
)
