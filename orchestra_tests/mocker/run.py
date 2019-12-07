import sys

import nibabel as nib

from os import path

# paths:
outpath = '/data/results/dummy_tumor_class.nii.gz'
t1 = '/data/t1.nii.gz'
t2 = '/data/t2.nii.gz'
t1c = '/data/t1c.nii.gz'
fla = '/data/flair.nii.gz'

# try to load all files
if path.isfile(t1) and path.isfile(t2) and path.isfile(t1c) and path.isfile(fla):
    seg = nib.load('dummy_segmentation.nii.gz')
    nib.save(seg, outpath)
else:
    print("Very grave error, not all files could be loaded!")
    sys.exit(7)
