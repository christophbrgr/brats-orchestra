#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for the fusion of Brain Tumor Scans 
# using the MICCAI BRATS algorithmic repository
# 
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.

import os
import scipy.io as spio
import numpy as np
import util.own_itk as oitk
import util.score as score
import util.filemanager as fmgnr
import errno
from pprint import pprint
from tqdm import tqdm

import SimpleITK as sitk

# global dimensions of segmentation volume
dim = (155,240,240)

def staple(segmentations, proto):
    estimate = np.zeros(dim, dtype=np.float64)
    stapler = sitk.STAPLEImageFilter()
    stapler.SetForegroundValue(1.0)
    segs = []
    for _, s in segmentations.items():
        segs.append(oitk.make_itk_image(s, proto))
    estimate = stapler.Execute(segs)
    return estimate

def setWeights(weighted=False, method='wt', directory=0, verbose=False):
    """ Receives a list of containers and the path to the 
    segmentation results, then matches the right result names
    to the passed container names and creates a dict with the 
    proper weights for the fusion methods.
    weights are determined based on the method used and the 
    dice score that is achieved by the containers on the training set
    input:  containers (list of container/algorithm-ids)
            method (fusion method to be used wt, at or ct, default is wt)
            directory (path to the segmentation results)
            verbose (terminal output yes or no)
    returns:    dictionary containing the weights with the result folder
                name pattern as key 

    """
    # TODO look up weights by dice-score in external file
    # static weights for testing
    if weighted:
        weights = {
            'istb_aj': 0.797171488,
            'brats_ac': 0.745408624,
            'changken1qtimlabbrats_final': 0.749367076,
            'ekrivovbrats2017_old': 0.748456509,
            'kamleshpbrats17': 0.70736689,
            'mikaelagnmagnrbm': 0.741016945,
            'sarassaras_test_brats_2017': 0.749367076,
            'gevaertlab': 0.74343376,
            'brats_dc': 0.7,
            'default': 0.7
        }
    else:
        weights = {
            'istb_aj': 1,
            'brats_ac': 1,
            'changken1qtimlabbrats_final': 1,
            'ekrivovbrats2017_old': 1,
            'kamleshpbrats17': 1,
            'mikaelagnmagnrbm': 1,
            'sarassaras_test_brats_2017': 1,
            'gevaertlab': 1,
            'qtimlab': 1,
            'brats_dc': 1,
            'isensee' : 1,
            'default': 1
        }
    return weights

def assembleFiles(directory, static_weights, t=0, verbose=True):
    """ Takes a list of container names, looks for the segmentation
    results and then loads each of them into a list of numpy arrays
    input:  filename (patient-id)
            containers (list of container ids)
            t (threshold for class border)
            static_weights (weights for static majority voting - 
                        should be 1 in first iteration of simple)
    returns a list of numpy arrays
    """
    # empty dicts for segmentations and weight, indeces are the algorithm
    # IDs
    segmentations = dict()
    weights = dict()
    i = 0
    #iterate through the directory
    for subdirs in os.listdir(directory):
        if not os.path.isdir(os.path.join(directory, subdirs)):
            continue # Not a directory
        #don't distinguish between upper- and lowercase
        #if 'brats' in subdirs or 'Brats' in subdirs:
        elif 'fusion' in subdirs:
            continue
        else:
            files = os.listdir(os.path.join(directory, subdirs))
            subdir = os.path.join(directory, subdirs)
            for file in files:
                if 'nii' in file:
                    if(verbose):
                        print('Segmentation number: ', i)
                        # print(os.path.join(subdir, file))
                    path = (os.path.abspath(os.path.join(subdir, file)))
                    if verbose:
                        print('Loading ITK image...')
                    temp = oitk.get_itk_image(path)
                    tmp = oitk.reduce_arr_dtype(oitk.get_itk_array(temp), False)
                    #binary file for whole tumor
                    result = np.zeros(tmp.shape)
                    if t == 1:
                        result[tmp == 1] = 1
                    elif t == 0:
                        result[tmp > 0] = 1
                    else:
                        result[tmp == 4] = 1
                    if verbose:
                        print('BIN SEG MAX:', tmp.max())
                        print('RESULT TMP MAX', result.max(), 'AND NONZERO Values', result.sum())
                    #append matching weight TODO
                    key = os.path.splitext(file)[0]
                    print('Directory: ', os.path.splitext(subdir)[0])
                    if verbose:
                        print('Key is: ', key)
                    #skip pointless segmentations (less than 500 voxels classified)
                    if result.sum() < 500:
                        continue
                    segmentations[key] = result
                    for d, value in static_weights.items():
                        if d in subdirs:
                            weights[key] = value
                            if verbose:
                                print('Appended weight', static_weights[d], 'to segmentation', subdirs, 'with algo', d, 'and key', key)
                    i += 1
                    pprint(weights)
    return segmentations, weights

def wtMajorityVote(segmentations, weights, verbose=True):
    """ Performs a majority vote fusion of an arbitrary number of
    segmentation results
    Compound: votes are fused to either 0 or 1 label (no tumor vs tumor)
    input: list of segmentations (numpy arrays)
    return: fused result as a numpy array
    """
    num = len(segmentations)
    # manage empty calls
    if num == 0:
        print('ERROR! No segmentations to fuse.')
        return np.zeros(dim)
    if verbose:
        print ('Number of segmentations to be fused using compound majority vote is: ', num)
    # load first segmentation and use it to create initial numpy arrays
    temp = next(iter(segmentations.values()))
    label = np.zeros(temp.shape)
    result = np.zeros(temp.shape)
    #loop through all available segmentations and tally votes
    for key, s in segmentations.items():
        # count every label greater than 0 = tumor
        label[s > 0] += 1.0*weights[key]
        if verbose:
            print('Weight for segmentation', key, 'is:', weights[key])
    if verbose:
        print('Tumor class > 0 Max and Min: ', label.max(), 
                                    label.min(), label.dtype)
    # create result and label it where the majority agreed
    num = sum(weights.values())
    if verbose:
        print('sum of all weights: ', num)
    result[label >= (num/2.0)] = 1
    if verbose: 
        print('Shape of result:', result.shape)
        print('Shape of current input array:', temp.shape)
        print('Labels and datatype of current input:', temp.max(), 
                                            temp.min(), temp.dtype)
    return result

def simple(segmentations, weights, t=0.05, stop=25, inc=0.07, verbose=True, 
        method='dice', iterations=25):
    """ Implementation of the SIMPLE algorithm
    Iterative weights estimation to find new weights for majority
    voting
    segmentations are discarded if the weights falls too far behind
    the expert segmentation (if score < t*max_score)
    Input:
    segmentations:  list of numpy arrays with segmentations
    weights:        initial weights for the first iteration
    t:              initial threshold value
    stop:           if the number of changed labels per 
                    iterations falls below this number, the
                    algorithm stops -> convergence
    inc:            increment for t after every iteration
                    (linear: t = t+inc)
    verbose:        Test output: True/False
    method:         Scoring method for performance 
                    estimation, for options see the 
                    documentation for customScore in score.py
    iterations:     max number of iterations before the algorithm stops
                    to keep the runtime bounded if there is no 
                    convergence

    Return:
    estimate:       Numpy label array with same shape as the input
                    = Fused Segmentation
    """
    # baseline estimate
    estimate = wtMajorityVote(segmentations, weights, verbose=verbose)
    #initial convergence baseline
    conv = np.sum(estimate)
    i = 0
    for i in range(iterations):
        if np.sum(estimate) == 0:
            return np.zeros(dim)
        if verbose:
            print('Tau is now:', t)
        for key, s in segmentations.items():
            # assign score to every segmentation
            weights[key] = score.customScore(s, estimate, method) #cube scores for brutal enhancement
            if verbose:
                print('Calculated score:', weights[key])
        # calculate maximum score
        max_phi = max(weights.values())
        entriesToRemove = []
        for key, w in weights.items():
            # check if a segmentation falls below the threshold
            if(w < t*max_phi):
                entriesToRemove.append(key)
                if verbose:
                    print('Will remove segmentation and weights score' +
                        'for element:', key)
        for k in entriesToRemove:
                segmentations.pop(k, None)
                weights.pop(k, None)
        if verbose:
            print('[STATUS] Now calculating a new estimate in iteration', i+1)
        estimate = wtMajorityVote(segmentations, weights, verbose=verbose)
        t = t+inc
        # check if it converges
        if np.abs(conv-np.sum(estimate)) < stop:
            break
        conv = np.sum(estimate)
    # when finished, return the result
    return estimate

def fuse(directory, method='simple', verbose=True):
    """ Overall fusion class, used to start any fusion process provided here
    Input parameters: 
        directory = directory containing patients and an arbitrary number
        of segmentation niftis
        method = simple for SIMPLE fusion (default)
                 majority for an unweighted majority voting
                 w_majority for a weighted majority voting
    Output: None, saves results to new file in every patient directory
    """
    # preprocess files to ensure functionality
    fmgnr.conversion(directory, verbose)
    # class borders between whole tumor, active tumor and tumor core
    evalclasses = {
        'wt': 0,
        'tc': 1,
        'at': 2
    }
    # class labels as stated in the paper
    labels = {
        'wt': 2, #edema
        'tc': 1, #tumor core NCR/NET
        'at': 4 # enhancing tumor
    }
    w = False
    if method == 'simple':
        iter = 25
    elif method == 'w_majority':
        iter = 0
        w = True
    else:
        iter = 0
    # set params depending on the method used
    #loop through brats dir
    for patient in tqdm(os.listdir(directory)):
        if not os.path.isdir(os.path.join(directory, patient)):
            continue # Not a directory
        if 'brats' in patient:
            patpath = os.path.join(directory, patient)
            a_weights = setWeights(weighted=w, method=evalclasses['wt'], directory=directory, verbose=verbose)
            # init array for result
            res = np.zeros(dim)
            #iterate through 3 tumor classes, then build final segmentation labels
            for key, value in evalclasses.items():
                if verbose:
                    print('[INFO] Now fusing the following region: ', key)
                segmentations, weights = assembleFiles(patpath, a_weights, t=value, verbose=verbose)
                #set fixed weights
                temp = simple(segmentations, weights, iterations=iter, method='dice')
                res[temp == 1] = labels[key]
            savepath = os.path.join(patpath, 'fusion')
            try:
                os.mkdir(savepath)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
                pass
            oitk.write_itk_image(oitk.make_itk_image(res), os.path.join(os.path.join(savepath,
                                    method + '_fusion.nii.gz')))

def testStaple():
    directory = '/Users/christoph/Documents/Uni/Bachelorarbeit/Testdaten/fusion_tests/brats2016_test_2013_patx116_1'
    a_weights = setWeights(weighted=False, method=0, directory=0, verbose=True)
    # load prototype images to get dimensions
    proto = oitk.get_itk_image('/Users/christoph/Documents/Uni/Bachelorarbeit/Testdaten/fusion_tests/brats2016_test_2013_patx116_1/brats2016_test_2013_patx116_1_romainsauvestregevaertlab/tumor_gevaertlab_class.nii')
    segs, _ = assembleFiles(directory, a_weights, verbose=True)
    #result = staple(segs, proto)
    dictlist = []
    for value in segs.items():
        dictlist.append(value)
    foregroundValue = 1
    threshold = 0.95
    reference_segmentation_STAPLE_probabilities = sitk.STAPLE(dictlist, foregroundValue) 
    reference_segmentation_STAPLE = reference_segmentation_STAPLE_probabilities > threshold
    oitk.write_itk_image(oitk.make_itk_image(reference_segmentation_STAPLE, proto), os.path.join(os.path.join(directory, 'staple_fusion.nii.gz')))
