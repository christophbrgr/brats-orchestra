from orchestra import segmentor, fusionator

seg = segmentor.Segmentor(config='orchestra/config/dockers_demo.json')
seg2 = segmentor.Segmentor()
fus = fusionator.Fusionator()

t1 = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t1.nii.gz'
t2 = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t2.nii.gz'
t1c ='/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t1ce.nii.gz'
flair = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/flair.nii.gz'
outpath = '/Users/christoph/Documents/Uni/HiWi/IBBM/BRATUM/Testdata/weborchestra/outputForOrc/file.nii.gz'
#seg2.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker2', outputPath=outpath)
#segmentor.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker', outputPath=None, verbose=True)
#seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker', outputPath=outpath)
#seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker', outputPath='file.nii.gz')
#fus.dirFuse('/Users/christoph/Desktop/brats_test')
#fus.dirFuse('/Users/christoph/Documents/Uni/HiWi/IBBM/BRATUM/Testdata/weborchestra/outputForOrc/')
segs = ['/Users/christoph/Desktop/brats_test/BraTS19_Testing_001_mars.nii.gz', '/Users/christoph/Desktop/brats_test/BraTS19_Testing_001_scan.nii.gz', '/Users/christoph/Desktop/brats_test/BraTS19_Testing_001_zyx.nii.gz']
weights=[1,2,1]
fus.fuse(segs, '/Users/christoph/Desktop/brats_test/BraTS19_Testing_fusion_weighted.nii.gz', method='simple', weights=weights)
# should error out on weight
weights.append(3)
try:
    fus.fuse(segs, '/Users/christoph/Desktop/brats_test/BraTS19_Testing_fusion_weighted.nii.gz', method='simple', weights=weights)
except Exception as e:
    print('Error occurred: ' + str(e))
    pass
# should error out on file error
segs.append('invalid/path/to/nifti/hello.nii.gz')
try:
    fus.fuse(segs, '/Users/christoph/Desktop/brats_test/BraTS19_Testing_fusion_weighted.nii.gz', method='simple', weights=weights)
except Exception as e: 
    print('Error occurred: ' + str(e))
    pass
seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mav', outputPath=outpath)
seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker2', outputPath=outpath)
