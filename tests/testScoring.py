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

import unittest
import numpy as np
import util.score as score

class TestScores(unittest.TestCase):
    """
    Simple tests to ensure correct scoring performance
    """
    def setUp(self):
        self.test = np.array([[1,0,0,1],[1,1,0,0],[1,0,1,1],[0,0,0,0]])
        self.truth = np.array([[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,0,0,1]])
        self.pred1 = np.array([[[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,0,0,1]],[[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,0,0,3]],[[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,0,0,1]],[[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,0,0,1]]])
        self.pred2 = np.array([[[0,1,1,0],[1,1,1,1],[1,1,0,1],[1,0,0,1]],[[1,0,0,1],[1,2,2,1],[0,3,1,1],[1,1,1,1]],[[0,0,0,0],[1,0,0,1],[1,0,0,1],[1,1,0,1]],[[1,1,0,1],[1,1,0,1],[1,1,0,1],[1,1,0,1]]])
    
    def testDice(self):
        self.assertEqual((2/3), score.customScore(self.test, self.truth, method='dice'))
    
    def testSpec(self):
        self.assertEqual(0.75, score.customScore(self.test, self.truth, method='spec'))

    def testSens(self):
        self.assertEqual(0.625, score.customScore(self.test, self.truth, method='sens'))

    def testDiceSymmetry(self):
        self.assertEqual(score.customScore(self.pred1, self.pred2, method='dice'), score.customScore(self.pred2, self.pred1, method='dice'))

if __name__ == '__main__':
    unittest.main(verbosity=2)
    