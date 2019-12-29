from orchestra import segmentor, fusionator

seg = segmentor.Segmentor(config='orchestra/config/dockers_demo.json', verbose=True)
seg2 = segmentor.Segmentor()
fus = fusionator.Fusionator()

t1 = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t1.nii.gz'
t2 = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t2.nii.gz'
t1c ='/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t1ce.nii.gz'
flair = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/flair.nii.gz'
outpath = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/outputForOrc/file.nii.gz'
print('Test 1')
seg.segment(t1, t1c, t2, flair, cid='mocker2', outputPath=outpath)
print('Test 2')
seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker2', outputPath=outpath)
#seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker', outputPath=None)
print('Test 3')
seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='simple', outputPath=outpath)
#seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker', outputPath='file.nii.gz')
#fus.dirFuse('/Users/christoph/Desktop/brats_test')
#fus.dirFuse('/Users/christoph/Documents/Uni/HiWi/IBBM/BRATUM/Testdata/weborchestra/outputForOrc/')
print('Test 4')
segs = ['/Users/christoph/Desktop/brats_test/BraTS19_Testing_001_mars.nii.gz', '/Users/christoph/Desktop/brats_test/BraTS19_Testing_001_scan.nii.gz', '/Users/christoph/Desktop/brats_test/BraTS19_Testing_001_zyx.nii.gz']
weights=[1,2,1]
fus.fuse(segs, '/Users/christoph/Desktop/brats_test/BraTS19_Testing_fusion_weighted.nii.gz', method='simple', weights=weights)
print('Test 5')
# should error out on weight
weights.append(3)
try:
    fus.fuse(segs, '/Users/christoph/Desktop/brats_test/BraTS19_Testing_fusion_weighted.nii.gz', method='simple', weights=weights)
except Exception as e:
    print('Error occurred: ' + str(e))
    pass
# should error out on file error
print('Test 6')
segs.append('invalid/path/to/nifti/hello.nii.gz')
try:
    fus.fuse(segs, '/Users/christoph/Desktop/brats_test/BraTS19_Testing_fusion_weighted.nii.gz', method='simple', weights=weights)
except Exception as e: 
    print('Error occurred: ' + str(e))
    pass
print('Test 7')
seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mav', outputPath=outpath)
print('Test 8')
seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker2', outputPath=outpath)
