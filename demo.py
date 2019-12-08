from orchestra import segmentor

seg = segmentor.Segmentor(config='orchestra/config/dockers_demo.json')

t1 = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t1.nii.gz'
t2 = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t2.nii.gz'
t1c ='/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t1ce.nii.gz'
flair = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/flair.nii.gz'
outpath = '/Users/christoph/Documents/Uni/HiWi/IBBM/BRATUM/Testdata/weborchestra/outputForOrc/file.nii.gz'
#segmentor.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker', outputPath=None, verbose=True)
#seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker', outputPath=outpath)
#seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mocker', outputPath='file.nii.gz')
seg.segment(t1=t1, t1c=t1c, t2=t2, fla=flair, cid='mav', outputPath=outpath)
