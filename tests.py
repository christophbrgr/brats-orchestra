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
import os
from orchestra import Orchestra

class TestOrchestraSetup(unittest.TestCase):
    """
    Testing my Orchestra, yeah
    """
    def testConfigSuccess(self):
        config = os.path.abspath('config.json')
        containers = os.path.abspath('containers.json')
        print('Testing Loading of Container ....')
        orchestra = Orchestra(containers, config)
        self.assertEqual('mic-dkfz', orchestra.getContainerName(index='mic-dkfz'))
    
    def testContainerCount(self):
        config = os.path.abspath('config.json')
        containers = os.path.abspath('containers.json')
        print('Testing Container Count...')
        orchestra = Orchestra(containers, config)
        self.assertEqual(4, orchestra.getNumberOfContainers())

    def testInvalidFile(self):
        directory = 'brr.json'
        config = 'coooo.json'
        with self.assertRaises(IOError):
            orchestra = Orchestra(directory, config)

class TestOrchestraDocker(unittest.TestCase):
    def testDockerSetup(self):
        self.assertEqual(1, 1, msg='Docker plugin missing')
    
    def runDummy(self):
        config = os.path.abspath('config-tests.json')
        containers = os.path.abspath('containers.json')
        orchestra = Orchestra(containers, config)
        self.assertTrue(orchestra.runDummyContainer())

    @unittest.skip('Not yet in use')
    def testRunSingleContainer(self):
        config = os.path.abspath('config-tests.json')
        containers = os.path.abspath('containers.json')
        orchestra = Orchestra(containers, config)
        directory = os.path.abspath('/Users/christoph/Documents/University/Uni/HiWi/IBBM/Testdata/Brats17_CBICA_AAM_1')
        self.assertTrue(orchestra.runContainer('econib', directory))


if __name__ == '__main__':
    unittest.main()
