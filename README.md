# brats-orchestra
BraTS ensemble code based on the Docker images used in the BraTS Challenge 2018

##### Author: Christoph Berger
##### Version: 0.1

This code was part of my Bachelor`s thesis submitted at the Technical University of Munich in October 2018. The version published here is in the process of being adapted and built into a more general purpose segmentation pipeline to support more inputs and greater modularity.

This code makes use of containers taken from the BraTS Algorithmic repository, which can be found here: https://github.com/BraTS/Instructions/

Further info regarding the BraTS challenge (rules, how to particpate, publications) can be found at the official homepage: https://www.med.upenn.edu/sbia/brats2018.html

Some of the fusion results are pre-published in this summarizing manuscript: https://arxiv.org/abs/1811.02629
Please contact me if you intend to use parts of this work for your research, we'd be thrilled to hear about it. 

Current functionality:
- `segment.py` is the front-end script to manage Docker containers for segmentation tasks and organises files to work with the containers
- `fusion/fusion.py` uses the resulting individual fusions to create a final result (using various methods)
- `util/` contains various scripts to manage files on the filesystem, calculate metrics for segmentation performance, load and store medical images and more

### Usage of segment.py
```
python3 segment.py /brats/dir/path/
```
`/brats/dir/path/` is the path where all subject folders are located, which must look like this:
- `/brats/dir/path/`
  - `pat123/`
    - `flair.nii.gz`
    - `t1.nii.gz`
    - `t2.nii.gz`
    - `t1c.nii.gz`
  - `pat456/`
    - `...`

And so on.. Resulting segmentations will be placed into `pat123/pat123_<algorithm>_results/tumor_<algorithm>_class.nii.gz`

### Requirements
You need to have a working installation of Docker running on your system. Also, install all other required packages for this code to run using:

```
pip install -r requirements.txt
```

### Current Tasks
- rebuild the configuration file system to use JSON and simplify I/O
- compatibility for automated GPU segmentation using Nvidia-Docker
