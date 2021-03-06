#!/usr/bin/env python

from setuptools import setup

setup(
    name="smartc",
    description="Smart contracts reengineered",
    version="0.0.1",
    author="Guillem Borrell",
    author_email="guillemborrell@gmail.com",
    packages=[
        'smartc',
        ],
    zip_safe=False,
    install_requires=['zmq', 'tornado', 'autobahn', 'graphviz'],
    include_package_data=True,
    setup_requires=['flake8'],
    tests_require=[]
    )
