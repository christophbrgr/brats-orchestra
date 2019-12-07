# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for the fusion of segmentation labels
#
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.
import os
import os.path as op
from .util import own_itk as oitk
from .util import filemanager as fm

class Fusionator(object):
    def __init__(self, method):
        self.method = method

    def mav(self, candidates, weights=None):
        return 0

    def simple(self, candidates, weights=None):
        return 0

    def dirFuse(self, directory):
        candidates = []
        weights = []
        for file in os.listdir(directory):
            if file.endswith('.nii.gz'):
                try:
                    candidates.append(oitk.get_itk_array(oitk.get_itk_image(op.join(directory, file))))
                    weights.append(1)
                    print('Loaded: ' + os.path.join(directory, file))
                except Exception as e:
                    print('VERY VERY BAD, this should be logged somewhere: ' + e)
    
    def fuse(self, outputPath):
        # load segmentations into list:
        candidates = []
        if self.method == 'mav':
            result = self.mav(candidates)
        elif self.method == 'simple':
            result = self.simple(candidates)
        else:
            pass

        return result
