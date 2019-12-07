from .orchestra import weborchestra as web

t1 = '/Users/christoph/Documents/Uni/HiWi/IBBM/BRATUM/Testdata/weborchestra/DE_RI_x00009-1/t1.nii.gz'
t2 = '/Users/christoph/Documents/Uni/HiWi/IBBM/BRATUM/Testdata/weborchestra/DE_RI_x00009-1/t2.nii.gz'
t1c ='/Users/christoph/Documents/Uni/HiWi/IBBM/BRATUM/Testdata/weborchestra/DE_RI_x00009-1/t1c.nii.gz'
flair = '/Users/christoph/Documents/Uni/HiWi/IBBM/BRATUM/Testdata/weborchestra/DE_RI_x00009-1/fla.nii.gz'
dir = '/Users/christoph/Documents/Uni/HiWi/IBBM/BRATUM/Testdata/weborchestra/DE_RI_x00009-1/results'
outpath = '/Users/christoph/Documents/Uni/HiWi/IBBM/BRATUM/Testdata/weborchestra/outputForOrc'
print(web._handleResult('hello', dir, outputPath=None))
web.segment(t1=t1, t2=t2, flair=flair, t1c=t1c, normalize=True, verbose=True, dev=True)
