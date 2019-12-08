# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for the fusion of segmentation labels
#
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.
import os
import logging

import numpy as np
import os.path as op
from .util import own_itk as oitk
from .util import filemanager as fm

class Fusionator(object):
    def __init__(self, method, verbose=True):
        self.method = method
        self.verbose = verbose

    def mav(self, candidates, weights=None):
        num = len(candidates)
        # manage empty calls
        if num == 0:
            print('ERROR! No segmentations to fuse.')
        if self.verbose:
            print ('Number of segmentations to be fused using compound majority vote is: ', num)
        labels = np.unique(candidates[0])
        # load first segmentation and use it to create initial numpy arrays
        temp = candidates[0]
        result = np.zeros(temp.shape)
        #loop through all available segmentations and tally votes for each class
        print(labels)
        for l in sorted(labels, reverse=True):
            label = np.zeros(temp.shape)
            for c, w in zip(candidates, weights):
                print('weight is: ' + str(w))
                label[c == l] += 1.0*w
            num = sum(weights)
            result[label >= (num/2.0)] = l
        print('Shape of result:', result.shape)
        print('Shape of current input array:', temp.shape)
        print('Labels and datatype of current input:', result.max(), 
                                            result.min(), result.dtype)
        return result

    def simple(self, candidates, weights=None):
        return 0

    def dirFuse(self, directory):
        candidates = []
        weights = []
        temp = None
        for file in os.listdir(directory):
            if file.endswith('.nii.gz'):
                temp = op.join(directory, file)
                try:
                    candidates.append(oitk.get_itk_array(oitk.get_itk_image(temp)))
                    weights.append(1)
                    print('Loaded: ' + os.path.join(directory, file))
                except Exception as e:
                    print('VERY VERY BAD, this should be logged somewhere: ' + e)
        if self.method == 'mav':
            result = self.mav(candidates, weights)
        elif self.method == 'simple':
            result = self.simple(candidates, weights)
        try:
            oitk.write_itk_image(oitk.make_itk_image(result, proto_image=oitk.get_itk_image(temp)), op.join(directory, self.method + '_fusion.nii.gz'))
            logging.info('Segmentation Fusion with method {} saved in directory {}.'.format(self.method, directory))
        except Exception as e:
            print('Very bad, this should also be logged somewhere: ' + str(e))
            logging.exception('Issues while saving the resulting segmentation: {}'.format(str(e)))
    
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
