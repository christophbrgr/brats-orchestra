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
import docker
import os

import util.filemanager as filemanager

class Orchestra(object):
    def __init__(self, config):
        """ Init the orchestra class with placeholders
        """
        self.noOfContainers = 0
        self.config = []
        self.directory = None
        self.verbose = True
        # setup docker api:
        # self.docker = docker.from_env()
        try: 
            configfile = open(config, 'r')
            self.config = json.load(configfile)
            self.noOfContainers = len(self.config.keys())
            configfile.close()
        except IOError as e: 
            print('I/O error({0}): {1}'.format(e.errno, e.strerror))
            raise
        except ValueError:
            print('Invalid configuration file')
            raise
        except:
            print('Unexpected Error!')
            raise

    def getContainerName(self, index):
        return self.config[index]['name']

    def getNumberOfContainers(self):
        return len(self.config)

    def runDummyContainer(self, stop=False):
        client = docker.from_env()
        container = client.containers.run('hello-world', detach=True)
        print(container.logs())
        if stop:
            container.stop()
        container.reload()
        return container.status, container

    def runContainer(self, id, directory):
        """
        Runs one container on one patient folder
        """
        try:
            client = docker.from_env()
            container_id = client.containers.run(id, command=self.config[id]['command'], volumes=[directory], host_config=client.create_host_config(binds=[self.config[id]['mountpoint'],]))
            container_id.logs()
            client.wait(container_id)
            # should the container not stop in time, it is manually stopped
            client.stop(container_id)
        except 	docker.errors.APIError as fail:
            print(fail)
            return False
        client.remove_container(container_id)
        print('Container run successful')
        return True



    def runIterate(self):
        """ Loads the config file with a list of available containers
        """
        # processes the config details
        for key, item in self.config.items():
            img_id = self.config[key]['id']
            # load the container command, default is empty
            command = self.config[key]['command']
            print(command)
            print(img_id)
            mount = '/data'
            # distinguish between a batch container (iterates over all
            # patients in the root directory by itself) and a standard
            # container (needs to be called for each patient individually)
            print('Total containers run: ', self.noOfContainers)


if __name__ == '__main__':
    config = os.path.abspath('config-tests.json')
    orchestra = Orchestra(config)
    status, container = orchestra.runDummyContainer()
    print(status)
