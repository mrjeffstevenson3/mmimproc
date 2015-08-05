import os


def deconstructRandparFiles(corrPfiles):
    matnames = []
    imgnames = []
    for corrPfile in corrPfiles:
        fields = os.path.basename(corrPfile).split('_')
        matname = '_'.join(fields[-5:-3])
        matname += '.mat'
        matnames.append(matname)
        imgname = '_'.join(fields[2:-5])
        imgname +='.nii.gz'
        imgnames.append(imgname)
    return (imgnames, matnames)
