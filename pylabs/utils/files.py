import os, glob


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
    
def deconstructFullRandparFiles(corrPfiles, matdir=None, imgdir=None):
    """Create dictionary of randpar input data files from list of results
    """
    combs = {}
    for corrPfile in corrPfiles:
    	fields = os.path.basename(corrPfile).split('.')[0]
        fields = fields.split('_')
        behavdescr = fields[-4]
        behavcol = fields[-5]
        behavcol = str(behavcol[3:5])
        modality = fields[-10]
        tstat = fields[-1]
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
        combs[imgname].append(behavdescr)
        combs[imgname].append(behavcol)
        combs[imgname].append(modality)
        combs[imgname].append(tstat)
        combs[imgname].append(corrPfile)
    return combs

def sortedParGlob (filefilter):
    return sorted(glob.glob(filefilter), key=lambda f: int(f.split('_')[-2]))
