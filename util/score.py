#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for evaluation and bulk segmentation of Brain Tumor Scans
# using the MICCAI BRATS algorithmic repository
# 
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.

import os
import scipy.io as spio
import numpy as np
import csv
import fnmatch
from natsort import natsorted
import collections
import sys
import math
import pandas 
import time
import pickle
from tqdm import tqdm

import util.filemanager as fmg
import util.own_itk as oitk
# import matlab.engine

#for testing only
root = '/Users/christoph/Documents/University/Uni/Bachelorarbeit/Testdaten/Complete_Results'
gt_root = '/Users/christoph/Documents/University/Uni/Bachelorarbeit/Testdaten/testing_nii_LABELS'

#dictionary for thresholds depending on the scoring method
thresh = {
    'wt': 0,
    'tc': 1,
    'at': 2
}

def customScore(seg, gt, method='dice'):
    """ Calculates a similarity score based on the
    method specified in the parameters
    Input: Numpy arrays to be compared, need to have the 
    same dimensions (shape)
    Default scoring method: DICE coefficient
    method may be:  'dice'
                    'auc'
                    'bdice'
    returns: a score [0,1], 1 for identical inputs
    """
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

def surfaceMask(gt, r, verbose=True):
    """
    Create a mask for the surface region for a given 
    circumference around the border of the volume
    Example: r=1
    Volume:     Mask (True/False)
    0 0 0 0 0 = F T F F F
    0 1 0 0 0 = T T T F F
    0 1 1 0 0 = T T T T F
    0 0 0 0 0 = F T T F F
    """
    # create a mask with the same shape as the input array
    mask = np.array(gt.shape(), dtype=np.bool)

    return mask
def surfaceDice(gt, seg, mask, verbose=True):
    try: 
        # True Positive (TP): we predict a label of 1 (positive) and the true label is 1.
        TP = np.sum(np.logical_and(np.logical_and(seg == 1, gt == 1), mask))
        # True Negative (TN): we predict a label of 0 (negative) and the true label is 0.
        TN = np.sum(np.logical_and(np.logical_and(seg == 0, gt == 0), mask))
        # False Positive (FP): we predict a label of 1 (positive), but the true label is 0.
        FP = np.sum(np.logical_and(np.logical_and(seg == 1, gt == 0), mask))
        # False Negative (FN): we predict a label of 0 (negative), but the true label is 1.
        FN = np.sum(np.logical_and(np.logical_and(seg == 0, gt == 1), mask))
        FPR = FP/(FP+TN)
        FNR = FN/(FN+TP)
        TPR = TP/(TP+FN)
        TNR = TN/(TN+FP)
    except ValueError:
        print('Value error encountered!')
        return 0
    # return DICE score for the surface region only
    return (2*TP/(2*TP+FP+FN))

def interRaterScore(root, score=None, method='at', verbose=True):
    """ Calculates and stores the DICE scores for all patients and 
    segmentations found in the passed directory
    Uses a ground truth file with 4 labels [0,1,2,4] which is expected
    to be named <method>_gt.nii.gz and in the patient directory
    (e.g. root/pat123/wt_gt.nii.gz)
    Binary scoring: whole tumor (wt): label 0 and labels > 0
                    tumor core (tc): label 0 and labels > 1
                    active tumor (at): label 0 and labels > 2
    Scoring method is specified via method parameter
    In:     root, path to segmentations and GT
            method, scoring method to use, see above
            verbose, output to the CLI or not
    Out:    Nothing
    """

    candidates = {
        'aju' : 'tumor_istb_aj_class.nii',
        'aca' : 'data_data_prediction.nii.gz',
        'kch' : 'tumor_qtimlab_class.nii.gz',
        'ekr' : 'tumor_00000000_class.nii.gz',
        'aka' : 'tumor_kamleshp_class.nii.gz',
        'mag' : 'tumor_magnrbm_class.nii',
        'sse' : 'tumor_saras_tb_class.nii.gz',
        'rsa': 'tumor_gevaertlab_class.nii',
        'gwa' : 'brats_dc_brats2016_test_klhd_pat101_3.nii.gz',
        'ise' : 'tumor_brats2017_isensee_class.nii.gz',
        'mav' : 'majvote_fusion.nii.gz',
        'sim' : 'simple_fusion.nii.gz',
        'sim2': 'simple2_fusion.nii.gz',
        'none' : 'default'
    }
    # preallocate dictionary space
    scores = {}
    # create indices for dataframes
    rows = list(candidates.keys())
    i = 0
    for patient in tqdm(os.listdir(root)):
        if not os.path.isdir(os.path.join(root, patient)):
            continue # Not a directory
        if 'brats' in patient:
            # create new dataframe
            patpath = os.path.join(root, patient)
            df = pandas.DataFrame(data=None, index=os.listdir(patpath), columns=os.listdir(patpath), dtype=float)
            #print('Current Patient: ', patient)
            # loop through patient folder
            for gt_folder in os.listdir(patpath):
                #print('Current GT Folder: ', gt_folder)
                # load arbitary ground truth file
                respath = os.path.join(patpath, gt_folder)
                paths = os.listdir(respath)
                for gt_cand in paths:
                    if fnmatch.fnmatch(gt_cand, '*.nii*'):
                        #print('GT is now: ', gt_cand)
                        gt_temp = oitk.get_itk_array(oitk.get_itk_image(os.path.join(respath, gt_cand)))
                        gt = np.zeros(gt_temp.shape)
                        #assemble final gt array
                        if method == 'tc':
                            #tumor core: may be labels 1,3,4
                            gt[gt_temp > 0] = 1
                            gt[gt_temp == 2] = 0
                        elif method == 'wt':
                            # whole tumor: labels 1,2,3,4 in participant's segmentation
                            gt[gt_temp > 0] = 1
                        else:
                            #active tumor
                            gt[gt_temp == 4] = 1
                for subfolder in os.listdir(patpath):
                    respath = os.path.join(patpath, subfolder)
                    paths = os.listdir(respath)
                    paths = natsorted(paths, key=lambda y: y.lower())
                    for result in paths:
                        # if there is a results file, load it and compute the dice score 
                        if fnmatch.fnmatch(result, '*.nii*'):
                            temp = oitk.get_itk_array(oitk.get_itk_image(os.path.join(respath, result)))
                            pred = np.zeros(temp.shape)
                            if method == 'tc':
                            #tumor core: may be labels 1,3,4
                                pred[temp > 0] = 1
                                pred[temp == 2] = 0
                            elif method == 'wt':
                                # whole tumor: labels 1,2,3,4 in participant's segmentation
                                pred[temp > 0] = 1
                            else:
                                #active tumor
                                pred[temp == 4] = 1
                            i = i+1
                            #gt_cand = gt_cand.translate({ord(i):None for i in '!/._-'})
                            #result = result.translate({ord(i):None for i in '!/._-'})
                            df[gt_folder][subfolder] = customScore(gt, pred, method='dice')
                scores[patient] = df

    with open('results.pkl', 'wb') as f:
        pickle.dump(scores, f, pickle.HIGHEST_PROTOCOL)

    """  Master Plan:

    for each patient: 
        for each result: 
            for each other file:
                getScore
                df[current-gt][current-seg] = score
        dict['patient'] = df
    """

def getScore(root, gt_root, score=None, file='gt.nii.gz', method='wt', verbose=True):
    """ Calculates and stores the DICE scores for all patients and 
    segmentations found in the passed directory
    Uses a ground truth file with 4 labels [0,1,2,4] which is expected
    to be named <method>_gt.nii.gz and in the patient directory
    (e.g. root/pat123/wt_gt.nii.gz)
    Binary scoring: whole tumor (wt): label 0 and labels > 0
                    tumor core (tc): label 0 and labels > 1
                    active tumor (at): label 0 and labels > 2
    Scoring method is specified via method parameter
    In:     root, path to segmentations and GT
            method, scoring method to use, see above
            verbose, output to the CLI or not
    Out:    Nothing
    """
    # load thresh, default is again 'wt' = 0
    t = thresh.get(method, 0)
    scores = dict()
    root = os.path.abspath(root)
    #open file for results
    try:
        f = open(os.path.join(root, method + '_scores.csv'), 'a')
    except IOError:
        print('Could not read file:' , method + '_scores.csv')
        sys.exit()

    for patient in os.listdir(root):
        if not os.path.isdir(os.path.join(root, patient)):
            continue # Not a directory
        if 'brats' in patient:
            patpath = os.path.join(root, patient)
            #TODO change loading to support GT for different methods
            gt_temp = oitk.get_itk_array(fmg.loadGT(gt_root, patient, file=file))
            gt = np.zeros(gt_temp.shape)
            if t == 1:
                # tumor core: labels 3 and 4
                gt[gt_temp > 2] = 1
            elif t == 0:
                #tissue is 1 in GT
                gt[gt_temp > 1] = 1
            else:
                # active tumor label 4
                gt[gt_temp == 4] = 1
            if verbose:
                print ('Sanity check of dimensions:', gt.shape)
                print ('Current patient:', patient)
                print ('GT max/min:', gt.max(), gt.min())
                #print ('Tumor Voxels: ', gt.sum())
            # init empty dictionary dimension
            scores[patient] = collections.OrderedDict()
            # loop through patient folder
            for result in os.listdir(patpath):
                if not os.path.isdir(os.path.join(patpath, result)):
                    continue # Not a directory
                # sort pathlist to get a pretty csv file
                respath = os.path.join(patpath, result)
                paths = os.listdir(respath)
                paths = natsorted(paths, key=lambda y: y.lower())
                for result in paths:
                    # if there is a results file, load it and compute the dice score 
                    if fnmatch.fnmatch(result, '*.nii*'):
                        temp = oitk.get_itk_array(oitk.get_itk_image(os.path.join(respath, result)))
                        pred = np.zeros(temp.shape)
                        if t == 1:
                            #tumor core: may be labels 1,3,4
                            pred[temp > 0] = 1
                            pred[temp == 2] = 0
                        elif t == 0:
                            # whole tumor: labels 1,2,3,4 in participant's segmentation
                            pred[temp > 0] = 1
                        else:
                            #active tumor
                            pred[temp == 4] = 1
                        if verbose: 
                            pass
                            # print ('Segmentation max/min:', pred.max(), pred.min())
                        dice = customScore(pred, gt, score)
                        # save dice score to dictionary
                        scores[patient][result] = dice
                        if verbose:
                            print('DICE Score for', result, 'is', dice)
            if verbose: 
                print('Current Scores:\n', scores[patient])
            #save scores to csv with proper prefix
            scores[patient] = collections.OrderedDict(sorted(scores[patient].items(), key=lambda t: t[0]))
            scores[patient]['patient'] = patient
            # with open(os.path.join(root, method + '_dice.csv'), 'a') as f:
            w = csv.DictWriter(f, scores[patient].keys())
            # if os.stat(os.path.join(root, method + '_dice.csv')).st_size == 0:
            w.writeheader()
            w.writerow(scores[patient])
    if verbose:
        print (scores)
    f.close()

def fullScore(s_dir='/Users/christoph/Documents/Uni/Bachelorarbeit/Testdaten/Complete_Results', gt_dir='/Users/christoph/Documents/Uni/Bachelorarbeit/Testdaten/testing_nii_LABELS'):
    getScore(s_dir, gt_dir, score='ppv', file='gt.nii', method='wt', verbose=True)
    getScore(s_dir, gt_dir, score='ppv', file='gt.nii', method='at', verbose=True)
    getScore(s_dir, gt_dir, score='ppv', file='gt.nii', method='tc', verbose=True)
    