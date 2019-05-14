#! ~/brats/virtualenvs/orchestra/bin/python
# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for evaluation and bulk segmentation of Brain Tumor Scans
# using the MICCAI BRATS algorithmic repository
#
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.

__version__ = '0.1'
__author__ = 'Christoph Berger'

from orchestra import Orchestra
import os

if __name__ == '__main__':
    #config = os.path.abspath('config-tests.json')
    config = os.path.abspath('config.json')
    orchestra = Orchestra(config)
    dir = os.path.abspath('~/brats/brats18/ATW_1_gr-b17-f')
    #status, container, client = orchestra.runDummyContainer()
    status = orchestra.runContainer('mic-dkfz', dir)
    print(status)