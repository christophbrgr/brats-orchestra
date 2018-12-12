#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for evaluation and bulk segmentation of Brain Tumor Scans
# using the MICCAI BRATS algorithmic repository
#
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.

__version__ = '0.0'
__author__ = 'Christoph Berger'

import os
import errno
import argparse
import configparser
import time
import datetime

import util.filemanager as filemanager
import docker

# parse arguments for input, output directories and flags
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Run all available containers with \
this base directory', action='store')
# args = parser.parse_args()
# Arranging paths
root = os.path.abspath(parser.parse_args().directory)
# initialize docker
#client = docker.Client()
client = docker.from_env()
# Expected modalities
modalities = ['flair.nii', 't1.nii', 't1c.nii', 't2.nii']
# Open file for timing data
try:
    log = open(os.path.join(root, 'time.txt'), mode='a')
except (OSError, IOError) as e:
    print('Opening log file failed: ' + str(e))

noOfContainers = 0
noOfRuns = 0

def assert_files(directory):
    """ Rudimentary checks to ensure a clean data set and the
    availability of the 4 required modalities
    """
    print('Looking for BRATS data directory..')
    for fn in os.listdir(directory):
        if not os.path.isdir(os.path.join(directory, fn)):
            continue # Not a directory
        if 'brats' in fn:
            print('Found pat data:', fn)
            print('Checking data validity now')
            files = os.listdir(os.path.join(directory, fn))
            assert set(modalities).issubset(files),\
            'Not all required files are present!'
    print('File check okay!')

def get_containers(config_file):
    """ Loads the config file with a list of available containers
    """
    global noOfContainers
    config = configparser.ConfigParser()
    config.read(config_file)
    # processes the config details
    for each_section in config.sections():
        img_id = config[each_section]['img_id']
        # load the container command, default is empty
        command = config[each_section].get('command',' ')
        print(command)
        mount = config[each_section]['mountpoint']
        # distinguish between a batch container (iterates over all
        # patients in the root directory by itself) and a standard
        # container (needs to be called for each patient individually)
        if config[each_section].getboolean('batch'):
            print('Found batch container: ', img_id)
            if config[each_section].getboolean('superresult'):
                try:
                    os.makedirs(os.path.join(root, 'results'))
                except OSError as err:
                    if err.errno != errno.EEXIST:
                        raise
            # check if the FLAIR modality is expected as flair.nii* or
            # as fla.nii* and rename the file accordingly
           if not config[each_section].getboolean('flair'):
                filemanager.rename_flair(root)
            else:
                filemanager.rename_fla(root)
            # if the code can't cope with more than the 4 standard
            # modalities in the directory, this is indicated with
            if config[each_section].getboolean('clean'):
                filemanager.remove_nii(root)
            else:
                filemanager.create_files(root)
            # run container with the specified input files
            run_container(img_id, command, root, mount)
            noOfContainers += 1
            # TODO: MKDIR results for batch container
            # the results folder is renamed to enable distinction
            rename_folder(img_id, root, 'res_br')
        else:
            print('Found standard container: ', img_id)
            if not config[each_section].getboolean('flair'):
                filemanager.rename_flair(root)
            else:
                filemanager.rename_fla(root)
            if config[each_section].getboolean('clean'):
                filemanager.remove_nii(root)
            else:
                filemanager.create_files(root)
            #  the iterative run script is called
            run_iterate(img_id, command, root, mount)
            noOfContainers += 1
        print('Total containers run: ', noOfContainers)

def rename_folder(name, folder, brats_id):
    """ Renames the results folder to the name of the
    docker container used to create it
    """
    # the following chars are removed to inhibit subdirectories
    chars_to_remove = ['/','.','\\','+']
    # create dictionary of the chars to remove for the translate method
    dd = {ord(c):None for c in chars_to_remove}
    name = brats_id + '_' + name.translate(dd)
    os.renames(os.path.join(folder, 'results'),
    os.path.join(folder, name))

def run_container(img_id, commands, folder, mount):
    """
    Runs the specified image using the docker api
    with the passed commands and a mount of the folder
    """
    # assemble mountpoint
    global noOfRuns
    noOfRuns += 1
    mountpoint = folder+':'+mount
    print(mountpoint)
    print('Starting execution now..')
    # start timing of execution
    start = time.time()
    # assemble a new container using the docker api
    container_id = client.create_container(img_id, command=commands,
    stdin_open=True, tty=True, volumes=[folder],
    host_config=client.create_host_config(binds=[mountpoint,]),
    detach=False)
    try:
        container_id = client.containers.run(img_id, command=commands, volumes=[folder],
        host_config=client.create_host_config(binds=[mountpoint,]), runtime=nvidia)
        # client.start(container_id, runtime=nvidia)
    except docker.errors.APIError as fail:
        print(fail)
    # wait for container to stop
    client.wait(container_id)
    try:
        # should the container not stop in time, it is manually stopped
        client.stop(container_id)
    except 	docker.errors.APIError as fail:
        print(fail)
    end = time.time()
    # the container (not needed anymore) is removed to clean the system
    client.remove_container(container_id)
    print('Container run successful')
    print('This run took', (end-start), 'seconds.')
    print('------------------- Total runs: ', noOfRuns,' ----------------')
    # write the relevant parameters to the logfile
    logstr = str('TIMESTAMP: ' + str(datetime.datetime.now()) +
     '\nContainer:' +str(img_id)+'\nPatient '+
     str(folder)+'\nTime: '+str(end-start)+'\n\n')
    log.write(logstr)

def run_iterate(img_id, command, directory, mount):
    """ Iterates through a given directory with subdirectories
    containing the four needed modalities and sends each matching
    subdirectory to the run_container function
    """
    print('Looking for BRATS data directories..')
    for fn in os.listdir(directory):
        if not os.path.isdir(os.path.join(directory, fn)):
            continue # Not a directory
        if 'brats' in fn:
            print('Found pat data: ', fn)
            try:
                os.makedirs(os.path.join(os.path.join(directory, fn),
                'results'))
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise
            print('Calling Container: ', img_id)
            run_container(img_id, command, os.path.join(directory, fn),
            mount)
            #rename folder and prepend pat_id
            rename_folder(img_id, os.path.join(directory, fn), fn)

#clean the entire input directory
#filemanager.completeclean(root)
# assert_files(root)
#filemanager.create_files(root, True)
# get the containers and start the segmentation
get_containers('config.txt')
# final cleanup
filemanager.rename_fla(root)
log.write('---------------Script run finished.----------------\n\n')
log.close()
# client.prune_containers() # Non-functional with new Docker version?
# client.prune_volumes()
