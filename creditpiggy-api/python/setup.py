#!/usr/bin/env python
from setuptools import setup, find_packages
setup(

	# Package name
    name = "creditpiggy",
    packages = [ 'creditpiggy' ],
    version = "0.1a1",

    # metadata for upload to PyPI
    author = "Ioannis Charalampidis",
    author_email = "ioannis.charalampidis@cern.ch",
    description = "CreditPiggy daemon interface library",
    license = "GPLv2",
    keywords = "creditpiggy library daemon interface",
    url = "https://github.com/wavesoft/creditpiggy",

)
