# brats-orchestra

BraTS ensemble code based on the Docker images used in the BraTS Challenge 2018

**Author: Christoph Berger**
**Version: 0.0.8**

## Prerequisites

### Installation

You have to have a working version of Docker on your system. If you don't, please download it [here](https://docs.docker.com/install/). Be sure to check if your Docker installation can actually use all necessary resources (esp. on Mac and Windows, there may be restrictions in the default installation, you can change those in the preferences).

```bash
git clone https://github.com/christophbrgr/brats-orchestra
cd brats-orchestra
pip install -e .
```

**Do keep in mind that some of the algorithms here have a very long processing time (e.g. an hour for one scan), so don't be surprised if your computer is nonresponsive during computations. We suggest running the code on a remote server to offload the computations.**

**All algorithms with GPU acceleration have been tested with a Nvidia Titan X or above GPU.** While we are pretty confident that most algorithms should also work on weaker machines, we'd like to point out that some failures may be causes by resource exhaustion.

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

Check the file `dockers.json` for a list of all available containers. This list can also be found [here.](https://github.com/BraTS/Instructions/blob/master/Repository_Links.md#brats-2018)

### Fusionator

The current implementation provides three methods for segmentation fusion:

1. General Majority Vote
2. Binary Majority Vote
3. SIMPLE (Selective and Iterative Method for Performance Level Estimation)

Generalized majority voting implicitly takes all the labels present in the passed candidate segmentations, fuses each label individually by employing majority voting and then returns a numpy array with the fused labels.
Binary majority voting uses the same principle but only works on binary labels (0 background, 1 foreground).
SIMPLE is an iterative method for performance estimation of candidate segmentations which employs binary majority voting to estimate performance.

**None of the methods employ any kind of domain knowledge which could improve performance. e.g. hierarchical labels.**

*CLI support for fusion comes soon.*

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

- error handling for failed segmentations
- please note that the test cases for the orchestra have not been updated yet (shame on me!)
