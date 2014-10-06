"""Set up for xblock-utils"""
import os
import os.path
from setuptools import setup

setup(
    name='xblock-utils',
    version='0.1a0',
    description='Various utilities for XBlocks',
    packages=[
        'xblockutils',
    ],
    install_requires=[
        'XBlock',
    ]
)
