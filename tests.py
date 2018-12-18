#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for evaluation and bulk segmentation of Brain Tumor Scans
# using the MICCAI BRATS algorithmic repository
#
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.

__version__ = '0.1'
__author__ = 'Christoph Berger'

import os
from orchestra import Orchestra

def orchestraInitTests():
    config = os.path.abspath('config.json')
    directory = os.path.abspath('directory.json')
    x = Orchestra(directory, config)
    Orchestra.printObject(x)

def orchestraDockerDry():
    config = os.path.abspath('config.json')
    directory = os.path.abspath('directory.json')
    x = Orchestra(directory, config)
    x.runContainers()

if __name__ == '__main__':
    orchestraInitTests()
    orchestraDockerDry()
