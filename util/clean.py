#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Cleans the specified directory (removes all nii.gz files, results and
subfolders)
"""
# Author: Christoph Berger
# Script for evaluation and bulk segmentation of Brain Tumor Scans 
# using the MICCAI BRATS algorithmic repository
# 
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.

__version__ = '0.0'
__author__ = 'Christoph Berger'

import os
import argparse
import util.filemanager as filemanager

# parse arguments for input, output directories and flags
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Clean everything in this directory', action='store')
# args = parser.parse_args()
# Arranging paths
root = os.path.abspath(parser.parse_args().directory)

#clean everything
filemanager.completeclean(root)
