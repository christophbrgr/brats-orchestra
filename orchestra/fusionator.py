# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for the fusion of segmentation labels
#
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.
import os
import logging
import itertools
import math

import numpy as np
import os.path as op
from .util import own_itk as oitk
from .util import filemanager as fm

class Fusionator(object):
    def __init__(self, method, verbose=True):
        self.method = method
        self.verbose = verbose

    def binaryMav(self, candidates, weights=None):
        '''
        Majority-voting for binary segmentation masks (0 background, 1 foreground)
        '''
        num = len(candidates)
        if weights == None:
            weights = itertools.repeat(1,num)
        # manage empty calls
        if num == 0:
            print('ERROR! No segmentations to fuse.')
        if self.verbose:
            print ('Number of segmentations to be fused using compound majority vote is: ', num)
        # load first segmentation and use it to create initial numpy arrays
        temp = candidates[0]
        result = np.zeros(temp.shape)
        #loop through all available segmentations and tally votes for each class
        label = np.zeros(temp.shape)
        for c, w in zip(candidates, weights):
            if c.max() != 1 or c.min() != 0:
                raise ValueError('The passed segmentation contains labels other than 1 and 0.')
            print('weight is: ' + str(w))
            label[c == 1] += 1.0*w
        num = sum(weights)
        result[label >= (num/2.0)] = 1
        print('Shape of result:', result.shape)
        print('Shape of current input array:', temp.shape)
        print('Labels and datatype of current input:', result.max(), 
                                            result.min(), result.dtype)
        return result

    def mav(self, candidates, weights=None):
        '''
        Majority voting for an arbitrary number of classes
        '''
        num = len(candidates)
        if weights == None:
            weights = itertools.repeat(1,num)
        # manage empty calls
        if num == 0:
            print('ERROR! No segmentations to fuse.')
        if self.verbose:
            print ('Number of segmentations to be fused using compound majority vote is: ', num)
        labels = np.unique(candidates[0])
        # remove background label
        if 0 in labels:
            labels = np.delete(labels, 0)
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
        print('Labels and datatype of result:', result.max(), 
                                            result.min(), result.dtype)
        return result

    def simple(self, candidates, weights=None, t=0.05, stop=25, inc=0.07, method='dice', iterations=25):
        '''
        SIMPLE implementation using DICE scoring

        Params:
        t: Tau value for dropout, candidate segmentations are removed if
            their weight is smaller than tau * (best score of current 
            iteration)
        stop:   convergence criterium, when less than 25 labels change during
                a given iteration, convergence is assumed and the iteration stops
        inc:    the increment by which tau increases with every iteration
        iterations: if no convergence is reached, this is the maximum number of 
                    iterations (per label!) until execution stops
        '''
        # manage empty calls
        num = len(candidates)
        if num == 0:
            print('ERROR! No segmentations to fuse.')
            raise IOError('No valid segmentations passed for SIMPLE Fusion')
        if self.verbose:
            print ('Number of segmentations to be fused using SIMPLE is: ', num)
        # handle unpassed weights
        if weights == None:
            weights = itertools.repeat(1,num)
        # get unique labels for multi-class fusion
        labels = np.unique(candidates[0])
        result = np.zeros(candidates[0].shape)
        # remove background label
        if 0 in labels:
            labels = np.delete(labels, 0)
        logging.info('Fusing a segmentation with the labels: {}'.format(labels))
        # loop over each label
        for l in sorted(labels):
            # load first segmentation and use it to create initial numpy arrays
            bin_candidates = [(c == l).astype(int) for c in candidates]
            print(bin_candidates[0].shape)
            # baseline estimate
            estimate = self.binaryMav(bin_candidates, weights)
            #initial convergence baseline
            conv = np.sum(estimate)
            # check if the estimate was reasonable
            if conv == 0:
                logging.error('Majority Voting in SIMPLE returned an empty array')
                return np.zeros(candidates[0].shape)
            # reset tau before each iteration
            tau = t
            for i in range(iterations):
                t_weights = [] # temporary weights
                for c in bin_candidates:
                    # score all canidate segmentations
                    t_weights.append((self._score(c, estimate, method)+1)**2) #SQUARED DICE!
                weights = t_weights
                # save maximum score in weights
                max_phi = max(weights)
                # remove dropout estimates
                bin_candidates = [c for c, w in zip(bin_candidates, weights) if (w > t*max_phi)]
                # calculate new estimate
                estimate = self.binaryMav(bin_candidates, weights)
                # increment tau 
                tau = tau+inc
                # check if it converges
                if np.abs(conv-np.sum(estimate)) < stop:
                    break
                conv = np.sum(estimate)
            # assign correct label to result
            result[estimate == 1] = l
        print('Shape of result:', result.shape)
        print('Shape of current input array:', bin_candidates[0].shape)
        print('Labels and datatype of current input:', result.max(), 
                                            result.min(), result.dtype)
        return result

    def dirFuse(self, directory, outputName=None):
        if self.method == 'all':
            return
        candidates = []
        weights = []
        temp = None
        for file in os.listdir(directory):
            if file.endswith('.nii.gz'):
                # skip existing fusions
                if 'fusion' in file:
                    continue
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
            if outputName == None:
                oitk.write_itk_image(oitk.make_itk_image(result, proto_image=oitk.get_itk_image(temp)), op.join(directory, self.method + '_fusion.nii.gz'))
            else:
                oitk.write_itk_image(oitk.make_itk_image(result, proto_image=oitk.get_itk_image(temp)), op.join(directory, outputName))
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
    
    def _score(self, seg, gt, method='dice'):
        ''' Calculates a similarity score based on the
        method specified in the parameters
        Input: Numpy arrays to be compared, need to have the 
        same dimensions (shape)
        Default scoring method: DICE coefficient
        method may be:  'dice'
                        'auc'
                        'bdice'
        returns: a score [0,1], 1 for identical inputs
        '''
        try: 
            # True Positive (TP): we predict a label of 1 (positive) and the true label is 1.
            TP = np.sum(np.logical_and(seg == 1, gt == 1))
            # True Negative (TN): we predict a label of 0 (negative) and the true label is 0.
            TN = np.sum(np.logical_and(seg == 0, gt == 0))
            # False Positive (FP): we predict a label of 1 (positive), but the true label is 0.
            FP = np.sum(np.logical_and(seg == 1, gt == 0))
            # False Negative (FN): we predict a label of 0 (negative), but the true label is 1.
            FN = np.sum(np.logical_and(seg == 0, gt == 1))
            FPR = FP/(FP+TN)
            FNR = FN/(FN+TP)
            TPR = TP/(TP+FN)
            TNR = TN/(TN+FP)
        except ValueError:
            print('Value error encountered!')
            return 0
        # faster dice? Oh yeah!
        if method is 'dice':
            # default dice score
            score = 2*TP/(2*TP+FP+FN)
        elif method is 'auc':
            # AUC scoring
            score = 1 - (FPR+FNR)/2
        elif method is 'bdice':
            # biased dice towards false negatives
            score = 2*TP/(2*TP+FN)
        elif method is 'spec':
            #specificity
            score = TN/(TN+FP)
        elif method is 'sens':
            # sensitivity
            score = TP/(TP+FN)
        elif method is 'toterr':
            score = (FN+FP)/(155*240*240)
        elif method is 'ppv':
            prev = np.sum(gt)/(155*240*240)
            temp = TPR*prev
            score = (temp)/(temp + (1-TNR)*(1-prev))
        else:
            score = 0
        if np.isnan(score) or math.isnan(score):
            score = 0
        return score
