#!/usr/bin/env python
# coding=utf-8
from setuptools import setup

setup(
    name='DroneSim',
    version='0.3.1',
    description=(
        'Yet Another Python API for SJTU Drone Contest.'
    ),
    author='DUT Hi-AI Lab',
    maintainer=[
        'YiChen Yuan',
        'Feilong Wang',
        'Bohan Tong',
        'Tianyu Wen',
        'Yingping Li'
    ],
    license='MIT License',
    packages=["dronesim"],
    platforms=["all"],
    classifiers=[
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    install_requires=[
        'msgpack-rpc-python',
        'numpy',
        'opencv-python>=4.1.0',
        'opencv-contrib-python>=4.1.0'
    ],
)
