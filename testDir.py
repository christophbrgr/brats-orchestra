from orchestra import segmentor, fusionator

seg = segmentor.Segmentor(config='orchestra/config/dockers_demo.json', verbose=True)

print('gets a valid absolute path')
t1 = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t1.nii.gz'
outpath = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/outputForOrc/file.nii.gz'
cid = 'mocker'
outputName, outputDir = seg._whereDoesTheFileGo(outpath, t1, cid)
print('Output name will be: {}'.format(outputName))
print('Output directory will be: {}'.format(outputDir))

print('gets None as outpath')
t1 = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t1.nii.gz'
outpath = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/outputForOrc/file.nii.gz'
cid = 'mocker'
outputName, outputDir = seg._whereDoesTheFileGo(None, t1, cid)
print('Output name will be: {}'.format(outputName))
print('Output directory will be: {}'.format(outputDir))

print('gets a filename only')
t1 = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t1.nii.gz'
outpath = 'segmentation_file.nii.gz'
cid = 'mocker'
outputName, outputDir = seg._whereDoesTheFileGo(outpath, t1, cid)
print('Output name will be: {}'.format(outputName))
print('Output directory will be: {}'.format(outputDir))

print('gets a relative path')
t1 = '/Testdata/BraTS19_CBICA_AQV_1/t1.nii.gz'
outpath = 'outputForOrc/file.nii.gz'
cid = 'mocker'
outputName, outputDir = seg._whereDoesTheFileGo(outpath, t1, cid)
print('Output name will be: {}'.format(outputName))
print('Output directory will be: {}'.format(outputDir))

print('gets path with ~ as outpath')
t1 = '/Users/christoph/Documents/Uni/HiWi/IBBM/Testdata/BraTS19_CBICA_AQV_1/t1.nii.gz'
outpath = '~/Documents/Uni/HiWi/IBBM/Testdata/outputForOrc/file.nii.gz'
cid = 'mocker'
outputName, outputDir = seg._whereDoesTheFileGo(outpath, t1, cid)
print('Output name will be: {}'.format(outputName))
print('Output directory will be: {}'.format(outputDir))