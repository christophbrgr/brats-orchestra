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

*You can also use all the segmentation and fusion features from the command line*
*This part is work in progress.*

## Other remarks

### Attribution

This software was created as part of the BraTUM.DB project and in the context of the Brain Tumor Segmentation challenge. Supported by Prof. Bjoern Menze, Florian Kofler and Dr. Benedikt Wiestler at the Technical University of Munich and the Department of Neuroradiology at the Clinic rechts der Isar in Munich. The BraTS Algroithmic Repository is a joint project with Spyridon Bakas of CBICA at the University of Pennsylvania, USA.

### Current Tasks

- log progress in containers
- error handling for failed segmentations
