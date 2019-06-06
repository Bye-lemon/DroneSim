#!/usr/bin/env python
# coding=utf-8
from setuptools import setup

setup(
    name='DroneSim',
    version=0.2,
    description=(
        'Yet Another Python API for SJTU Drone Contest.'
    ),
    author='DUT Drone Lab',
    maintainer='Yuan Yichen',
    license='MIT License',
    packages=["pack"],
    platforms=["all"],
    classifiers=[
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    install_requires=[
        'msgpack-rpc-python',
        'numpy',
    ],
)
