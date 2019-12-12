# -*- coding: utf-8 -*-
# Author: Christoph Berger
# Script for evaluation and bulk segmentation of Brain Tumor Scans
# using the MICCAI BRATS algorithmic repository
#
# Please refer to README.md and LICENSE.md for further documentation
# This software is not certified for clinical use.

import sys
import subprocess
import pprint 
import argparse

from orchestra import segmentor
from orchestra import fusionator

def list_dockers():
    seg = segmentor.Segmentor()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(seg.config)

def list_docker_ids():
    seg = segmentor.Segmentor()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(seg.config.keys())

def list_docker_gpu():
    seg = segmentor.Segmentor()
    print('all these images support GPU computations:')
    for id in seg.config.keys():
        if id['runtime'] == 'nvidia':
            print(id)

def list_docker_cpu():
    seg = segmentor.Segmentor()
    print('all these images support CPU computations:')
    for id in seg.config.keys():
        if id['runtime'] == 'runc':
            print(id)

def fusion():
    parser = argparse.ArgumentParser(description='Runs the Docker orchestra to fuse segmentations. All inputs have to have equal shape and label values')
    parser.add_argument('-i','--input', required=True,
                        help = 'Input directory containing all .nii.gz files to be fused')
    parser.add_argument('-m','--method', required=True,
                        help = 'Method for fusion: mav for majority voting, simple for SIMPLE')
    parser.add_argument('-o', '--output',
                        help = 'Filename for the output in format filename.nii.gz')
    parser.add_argument('-v', '--verbose',action='store_true',
                        help = 'Verbose mode outputs log info to the command line.')
    try:
            args = parser.parse_args()
    except SystemExit as e:
        if e.code == 2:
            parser.print_help()
        sys.exit(e.code)
    try:
        # runs the segmentation with all the settings wished for by the user
        fus = fusionator.Fusionator(method=args.method, verbose=args.verbose)
        fus.dirFuse(args.input, outputName=args.output)
    except subprocess.CalledProcessError as e:
        # Ignoring errors happening in the Docker Process, otherwise we'd e.g. get error messages on exiting the Docker via CTRL+D.
        pass
    except Exception as e:
        print('ERROR DETAIL: ', e)

def segmentation():
    parser = argparse.ArgumentParser(description='Runs the Docker orchestra to segment and fuse segmentations based on the' \
                                             'BraTS algorithmic repository' \
                                             'Please keep in mind that some models require Nvidia-Docker to run as' \
                                             ' they need a supported GPU.')
    parser.add_argument('-l', '--list',
                        help = 'List all models available for segmentation.',
                        action = 'store_true')
    parser.add_argument('-ll', '--longlist',
                        help = 'List all models available for segmentation with details.',
                        action = 'store_true')
    parser.add_argument('-lc', '--cpulist',
                        help = 'List all models supporting cpus.',
                        action = 'store_true')
    parser.add_argument('-lg', '--gpulist',
                        help = 'List all models supporting gpus.',
                        action = 'store_true')
    parser.add_argument('-t1',required=True,
                        help = 'Path to the t1 modality.')
    parser.add_argument('-t1c',required=True,
                        help = 'Path to the t1c modality.')
    parser.add_argument('-t2',required=True,
                        help = 'Path to the t2 modality.')
    parser.add_argument('-fla',required=True,
                        help = 'Path to the fla modality.')
    parser.add_argument('-d', '--docker', required=True,
                        help = 'Container ID or method used for fusion. (mav, simple, all). Run brats-orchestra --list to display all options.')
    parser.add_argument('-o', '--output',required=True,
                        help = 'Path to the desired output file.')
    parser.add_argument('-v', '--verbose',action='store_true',
                        help = 'Verbose mode outputs log info to the command line.')
    parser.add_argument('-c', '--config',
                        help = 'Add a path to a custom config file for dockers here.')
    parser.add_argument('-g', '--gpu', action='store_true',
                        help = 'Pass this flag if your Docker version already supports the --gpus flag.')
    try:
        if '-l' in sys.argv[1:] or '--list' in sys.argv[1:]:
            list_docker_ids()
            sys.exit(0)
        elif '-ll' in sys.argv[1:] or '--longlist' in sys.argv[1:]:
            list_dockers()
            sys.exit(0)
        elif '-lg' in sys.argv[1:] or '--gpulist' in sys.argv[1:]:
            list_docker_gpu()
            sys.exit(0)
        elif '-lc' in sys.argv[1:] or '--cpulist' in sys.argv[1:]:
            list_docker_cpu()
            sys.exit(0)
        else:
            args = parser.parse_args()
    except SystemExit as e:
        if e.code == 2:
            parser.print_help()
        sys.exit(e.code)
    try:
        # runs the segmentation with all the settings wished for by the user
        seg = segmentor.Segmentor(config=args.config, verbose=args.verbose, newdocker=args.gpu)
        seg.segment(t1=args.t1, t1c=args.t1c, t2=args.t2, fla=args.fla, cid=args.docker, outputPath=args.output)
    except subprocess.CalledProcessError as e:
        # Ignoring errors happening in the Docker Process, otherwise we'd e.g. get error messages on exiting the Docker via CTRL+D.
        pass
    except Exception as e:
        print('ERROR DETAIL: ', e)

if __name__ == '__main__':
    segmentation()