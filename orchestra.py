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

import sys
from pprint import pprint
import json

import util.filemanager as filemanager

class Orchestra(object):
    def __init__(self, directory, config):
        """ Init the orchestra class with placeholders
        """
        self.noOfContainers = 0
        self.containers = []
        self.config = []
        self.directory = None
        self.verbose = True
        try: 
            containerfile = open(directory, 'r')
            configfile = open(config, 'r')
            self.containers = json.load(containerfile)
            self.config = json.load(configfile)
            self.noOfContainers = len(self.containers.keys())
        except IOError as e: 
            print('I/O error({0}): {1}'.format(e.errno, e.strerror))
        except ValueError:
            print('Invalid configuration file')
        except:
            print('Unexpected Error!')
            raise

    def printObject(self):
        """ Print the object contents for debugging
        """
        print('The containers to run:')
        pprint(self.containers)
        print('The config file contents:')
        pprint(self.config)

    def runContainers(self):
        """ Loads the config file with a list of available containers
        """
        # processes the config details
        for key, item in self.config.items():
            img_id = self.containers[key]['id']
            # load the container command, default is empty
            command = self.containers[key]['command']
            print(command)
            print(img_id)
            mount = '/data'
            # distinguish between a batch container (iterates over all
            # patients in the root directory by itself) and a standard
            # container (needs to be called for each patient individually)
            print('Total containers run: ', self.noOfContainers)
