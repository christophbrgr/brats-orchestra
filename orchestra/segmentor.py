# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for evaluation and bulk segmentation of Brain Tumor Scans
# using the MICCAI BRATS algorithmic repository
#
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.

__version__ = '0.1'
__author__ = 'Christoph Berger'

import json
import subprocess
import os
import errno
import sys
import tempfile
import glob
import logging

import os.path as op
import numpy as np

from .util import own_itk as oitk
from .util import filemanager as fm
from . import fusionator


class Segmentor(object):
    '''
    Now does it all!
    '''
    def __init__(self, config=None, fileformats=None, verbose=True, tty=False, newdocker=True, gpu='0'):
        ''' Init the orchestra class with placeholders
        '''
        self.noOfContainers = 0
        self.config = []
        self.directory = None
        self.verbose = verbose
        self.tty = tty
        self.dockerGPU = newdocker
        self.gpu =gpu
        self.package_directory = op.dirname(op.abspath(__file__))
        # set environment variables to limit GPU usage
        os.environ['CUDA_DEVICE_ORDER']='PCI_BUS_ID'   # see issue #152
        os.environ['CUDA_VISIBLE_DEVICES']=gpu
        if config is None: 
            config = op.join(self.package_directory, 'config', 'dockers.json')
        if fileformats is None:
            self.fileformats = op.join(self.package_directory, 'config', 'fileformats.json')
        else:
            self.fileformats = fileformats
        try:
            configfile = open(config, 'r')
            self.config = json.load(configfile)
            self.noOfContainers = len(self.config.keys())
            configfile.close()
        except IOError as e:
            logging.exception('I/O error({0}): {1}'.format(e.errno, e.strerror))
            raise
        except ValueError:
            logging.exception('Invalid configuration file')
            raise
        except:
            logging.exception('Unexpected Error!')
            raise

    def getFileFormat(self, index):
        return self.config[index]['fileformat']

    def getContainerName(self, index):
        return self.config[index]['name']

    def getNumberOfContainers(self):
        return len(self.config)

    def runDummyContainer(self, stop=False):
        command = 'docker run --rm -it hello-world'
        subprocess.check_call(command, shell = True)

    def runContainer(self, id, directory):
        '''
        Runs one container on one patient folder
        '''
        if self.tty:
            command = ' docker run --rm -it '
        else:
            command = ' docker run --rm '
        if self.config[id]['runtime'] == 'nvidia':
            if self.dockerGPU:
                command = command + '--gpus all -e CUDA_VISIBLE_DEVICES='+str(self.gpu)+' -v ' + str(directory) + ':' + str(self.config[id]['mountpoint']) + ' ' + str(self.config[id]['id']) + ' ' + str(self.config[id]['command'])
            else:
                command = command + '--runtime=nvidia -e CUDA_VISIBLE_DEVICES='+str(self.gpu)+' -v ' + str(directory) + ':' + str(self.config[id]['mountpoint']) + ' ' + str(self.config[id]['id']) + ' ' + str(self.config[id]['command'])
        else:
            command = command + '-v ' + str(directory) + ':' + str(self.config[id]['mountpoint']) + ' ' + str(self.config[id]['id']) + ' ' + str(self.config[id]['command'])
        try:
            subprocess.check_call(command, shell = True)
        except Exception as e:
            logging.error('Segmentation failed for case {} with error: {}'.format(directory, e))
            if 'exit status 125' in str(e):
                logging.error('DOCKER DAEMON not running! Please start your Docker runtime.')
                sys.exit(125)
        if self.verbose:
            logging.info('Container exited without error')
        return True

    def runIterate(self, dir, cid):
        ''' Iterates over a directory and runs the segmentation on each patient found
        '''
        logging.info('Looking for BRATS data directories..')
        for fn in os.listdir(dir):
            if not os.path.isdir(os.path.join(dir, fn)):
                continue # Not a directory
            if 'DE_RI' in fn:
                logging.info('Found pat data: {}'.format(fn))
                try:
                    os.makedirs(os.path.join(os.path.join(dir, fn),
                    'results'))
                except OSError as err:
                    if err.errno != errno.EEXIST:
                        raise
                logging.info('Calling Container: {}'.format(cid))
                if not self.runContainer(cid, os.path.join(dir, fn)):
                    logging.info('ERROR: Run failed for patient {} with container {}'.format(fn, cid))
                    return False
                #TODO: rename folder and prepend pat_id
                #rename_folder(img_id, os.path.join(directory, fn), fn)
        return True

    def multiSegment(self, tempDir, inputs, method, outputName, outputDir):
        '''
        Runs all containers on a given input
        '''
        logging.debug('CALLED MULTISEGMENT')
        fusion = fusionator.Fusionator()
        for cid in self.config.keys():
            # replace this with a call to single-segment
            logging.info('[Orchestra] Segmenting with ' + cid)
            ff = self._format(self.getFileFormat(cid), self.fileformats)
            for key, img in inputs.items():
                savepath = op.join(tempDir, ff[key])
                img = oitk.get_itk_image(img)
                if self.verbose:
                    logging.info('[Weborchestra][Info] Writing to path {}'.format(savepath))
                oitk.write_itk_image(img, savepath)
            if self.verbose:
                logging.info('[Weborchestra][Info] Images saved correctly')
                logging.info('[Weborchestra][Info] Starting the Segmentation with one container now')
            status = self.runContainer(cid, tempDir)
            if status:
                if self.verbose:
                    logging.info('[Weborchestra][Success] Segmentation saved')
                resultsDir = op.join(tempDir, 'results/')
                saveLocation = op.join(outputDir, cid + '_tumor_seg.nii.gz')
                resultsDir = self._handleResult(cid, resultsDir, outputPath=saveLocation)
            else:
                logging.exception('Container run for CID {} failed!'.format(cid))
        fusion.dirFuse(outputDir, method=method, outputName=outputName)
    
    def singleSegment(self, tempDir, inputs, cid, outputName, outputDir):
        '''
        Segments the passed input with one container
        '''
        ff = self._format(self.getFileFormat(cid), self.fileformats)
        for key, img in inputs.items():
            savepath = op.join(tempDir, ff[key])
            img = oitk.get_itk_image(img)
            if self.verbose:
                logging.info('[Weborchestra][Info] Writing to path {}'.format(savepath))
            oitk.write_itk_image(img, savepath)
        if self.verbose:
            logging.info('[Weborchestra][Info] Images saved correctly')
            logging.info('[Weborchestra][Info] Starting the Segmentation with {} now'.format(cid))
        status = self.runContainer(cid, tempDir)
        if status:
            if self.verbose:
                logging.info('[Weborchestra][Success] Segmentation saved')
            resultsDir = op.join(tempDir, 'results/')
            resultsDir = self._handleResult(cid, resultsDir, outputPath=op.join(outputDir, outputName))
            # delete tmp directory if result was saved elsewhere
            return resultsDir
        if self.verbose:
            logging.error('[Weborchestra][Error] Segmentation failed, see output!')
        return None


    def segment(self, t1=None, t1c=None, t2=None, fla=None, cid='mocker', outputPath=None):
        outputDir = op.dirname(outputPath)
        outputName = op.basename(outputPath)
        if outputPath is not None:
            os.makedirs(outputDir, exist_ok=True)
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=op.join(outputDir, 'segmentor.log'),level=logging.DEBUG)
        logging.debug('DIRNAME is: ' + outputDir)
        logging.debug('FILENAME is: ' + outputName)
        logging.info('Now running a new set of segmentations on input: {}'.format(op.dirname(t1)))
        # switch between 
        inputs = {'t1':t1, 't2':t2, 't1c':t1c, 'fla':fla}
        # create temporary directory for storage
        storage = tempfile.TemporaryDirectory(dir=self.package_directory)
        tempDir = op.abspath(storage.name)
        resultsDir = op.join(tempDir, 'results')
        os.mkdir(resultsDir)
        logging.debug(tempDir)
        logging.debug(resultsDir)

        if cid == 'mav' or cid == 'simple' or cid == 'all':
            # segment with all containers
            logging.info('Called singleSegment with method: ' + cid)
            self.multiSegment(tempDir, inputs, cid, outputName, outputDir)
        else:
            # segment only with a single container
            logging.info('Called singleSegment with docker: ' + cid)
            self.singleSegment(tempDir, inputs, cid, outputName, outputDir)

    ### Private utility methods below ###

    def _handleResult(self, cid, directory, outputPath):
        '''
        This function handles the copying and renaming of the
        Segmentation result before returning
        '''
        # Todo: Find segmentation result
        contents = glob.glob(op.join(directory,'*'+cid+'*.nii*'))
        if len(contents) == 0:
            contents = glob.glob(op.join(directory,'*tumor*.nii*'))
        if len(contents) < 1:
            logging.error('[Weborchestra - Filehandling][Error] No segmentation saved, the container run has most likely failed.')
        elif len(contents) > 1:
            logging.error('[Weborchestra - Filehandling][Warning] Multiple Segmentations Found')
            img = oitk.get_itk_image(contents[0])
        img = oitk.get_itk_image(contents[0])
        if outputPath != None:
            os.makedirs(op.basename(outputPath), exist_ok=True)
            savePath = outputPath
            logging.info('Saving to the user-specified directory: {}'.format(savePath))
        else:
            savePath = op.join(directory, 'tumor_segm.nii.gz')
            logging.info('Saving to the temporary directory: {}'.format(savePath))
        oitk.write_itk_image(img, savePath)
        return savePath

    def _format(self, fileformat, configpath, verbose=True):
        # load fileformat for a given container
        try:
            configfile = open(op.abspath(configpath), 'r')
            config = json.load(configfile)
            configfile.close()
        except IOError as e:
            logging.exception('I/O error({0}): {1}'.format(e.errno, e.strerror))
            raise
        except ValueError:
            logging.exception('Invalid configuration file')
            raise
        except:
            logging.exception('Unexpected Error!')
            raise
        logging.info('[Weborchestra][Success]Loaded fileformat: {}'.format(config[fileformat]))
        return config[fileformat]

