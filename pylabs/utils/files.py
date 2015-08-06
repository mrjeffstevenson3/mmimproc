import os


def deconstructRandparFiles(corrPfiles, matdir=None, imgdir=None):
    """Create dictionary of image + matfiles combinations from list of results
    """
    combs = {}
    for corrPfile in corrPfiles:
        fields = os.path.basename(corrPfile).split('_')
        matname = '_'.join(fields[-5:-3])
        matname += '.mat'
        imgname = '_'.join(fields[2:-5])
        imgname +='.nii.gz'
        if matdir:
            matname = os.path.join(matdir, matname)
        if imgdir:
            imgname = os.path.join(imgdir, imgname)
        if not imgname in combs:
            combs[imgname] = []
        combs[imgname].append(matname)
    return combs
