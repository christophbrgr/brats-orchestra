# brats-orchestra
BraTS ensemble code based on the Docker images used in the BraTS Challenge 2018

*Author: Christoph Berger*
*Version: 0.0.8*

## Prerequisites

### Requirements

You need to have a working installation of Docker running on your system. Also, install all other required packages for this code to run using:

```bash
pip install -r requirements.txt
```

### Installation

```bash
git clone https://github.com/christophbrgr/brats-orchestra
cd brats-orchestra
pip install -e .
```

## Usage instructions

The package contains two modules, the Segmentor and the Fusionator:

### Segmentor

This module can be used to segment files using the BraTS Algorithmic Repository. You pass 4 modalities preprocessed to conform to the BraTS standard (you can use the BraTS Preprocessor for that), an algorithm-id to specifiy which container should segment your images and an output path (including a filename!).

```python
from orchestra import segmentor
seg = segmentor.Segmentor()
# t1 and so on are paths to niftis, ouputpath should also be a nifti
seg.segment(t1, t2, t1c, fla, cid='mocker', outputPath)
```

### Fusionator

*This part is work in progress* 

### Command Line Interface

*You can also use all the segmentation and fusion features from the command line, just try it for yourself after installing the module.*

```bash
(orchestra) Christophs-MBP:brats-orchestra christoph$ python orchestra/cli.py 
cli.py: error: the following arguments are required: -t1, -t1c, -t2, -fla, -d/--docker, -o/--output
usage: cli.py [-h] [-l] -t1 T1 -t1c T1C -t2 T2 -fla FLA -d DOCKER -o OUTPUT
              [-v] [-c CONFIG] [-g]

Runs the Docker orchestra to segment and fuse segmentations based on theBraTS
algorithmic repositoryPlease keep in mind that some models require Nvidia-
Docker to run as they need a supported GPU.

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            List all models available for segmentation.
  -t1 T1                Path to the t1 modality.
  -t1c T1C              Path to the t1c modality.
  -t2 T2                Path to the t2 modality.
  -fla FLA              Path to the fla modality.
  -d DOCKER, --docker DOCKER
                        Container ID or method used for fusion. (mav, simple,
                        all). Run brats-orchestra --list to display all
                        options.
  -o OUTPUT, --output OUTPUT
                        Path to the desired output file.
  -v, --verbose         Verbose mode outputs log info to the command line.
  -c CONFIG, --config CONFIG
                        Add a path to a custom config file for dockers here.
  -g, --gpu             Pass this flag if your Docker version already supports
                        the --gpus flag.
```

## Other remarks

### Attribution

This software was created as part of the BraTUM.DB project and in the context of the Brain Tumor Segmentation challenge. Supported by Prof. Bjoern Menze, Florian Kofler and Dr. Benedikt Wiestler at the Technical University of Munich and the Department of Neuroradiology at the Clinic rechts der Isar in Munich. The BraTS Algroithmic Repository is a joint project with Spyridon Bakas of CBICA at the University of Pennsylvania, USA.

### Current Tasks

- log progress in containers
- error handling for failed segmentations
