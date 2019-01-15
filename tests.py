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
import docker
import importlib
from orchestra import Orchestra

class TestOrchestraSetup(unittest.TestCase):
    """
    Testing my Orchestra, yeah
    """
    def testConfigSuccess(self):
        config = os.path.abspath('config.json')
        #print('Testing Loading of Container.. ')
        orchestra = Orchestra(config)
        self.assertEqual('mic-dkfz', orchestra.getContainerName(index='mic-dkfz'))
    
    def testContainerCount(self):
        config = os.path.abspath('config.json')
        #print('Testing Container Count...')
        orchestra = Orchestra(config)
        self.assertEqual(4, orchestra.getNumberOfContainers())

    def testInvalidFile(self):
        config = 'coooo.json'
        with self.assertRaises(IOError):
            orchestra = Orchestra(config)
    
class TestDocker(unittest.TestCase):
    """
    Docker infrastructure and functional tests
    No segmentation yet
    """
    @unittest.expectedFailure
    def testTests(self):
        self.assertEqual(1, 2, msg='Dummy testcases successfully failed!')

    def testDockerSetup(self):
        self.assertEqual(1, 1, msg='Docker plugin missing')

    def runDummySuccess(self):
        config = os.path.abspath('config-tests.json')
        orchestra = Orchestra(config)
        status, container = orchestra.runDummyContainer()
        print(status)
        print(container.status)
        container.stop()
        self.assertEqual('running', status, msg='Docker not able to run a container!')

    @unittest.skip('not yet in use')
    def runDummyFailure(self):
        config = os.path.abspath('config-tests.json')
        orchestra = Orchestra(config)
        status, container = orchestra.runDummyContainer(stop=True)
        print(status)
        print(container.status)
        container.stop()
        self.assertEqual('running', status, msg='Docker not able to run a container!')


    @unittest.skip('Not yet in use')
    def testRunSingleContainer(self):
        config = os.path.abspath('config-tests.json')
        orchestra = Orchestra(config)
        directory = os.path.abspath('/Users/christoph/Documents/University/Uni/HiWi/IBBM/Testdata/Brats17_CBICA_AAM_1')
        self.assertTrue(orchestra.runContainer('econib', directory))


if __name__ == '__main__':
    unittest.main()
