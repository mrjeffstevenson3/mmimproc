import os, warnings
import numpy
import nibabel
from scipy.optimize import curve_fit
from numpy import exp, cos, sin
from pylabs.utils import progress
from datetime import datetime


def irformula(x, a, b, c):
    return numpy.abs(a * (1 - b * exp(-x/c)))

def spgrformula(x, a, b):
    TR = spgrformula.TR
    return a * ((1-exp(-TR/b))/(1-cos(x)*exp(-TR/b))) * sin(x)

def t1fit(files, X, TR=None, nmaskfile=None, scantype='IR', t1filename=None, 
    voiCoords=None):
    
    import pdb
    pdb.set_trace()

    if t1filename is None:
        t1filename = 't1_fit.nii.gz'

    if isinstance(files, basestring):
        anImg = nibabel.load(files)
        imageDimensions = anImg.shape[:-1]
        data = [anImg.get_data()[...,i].ravel() for i in range(anImg.shape[-1])]
    else:
        anImg = nibabel.load(files[0])
        imageDimensions = anImg.shape 
        data = [nibabel.load(f).get_data().ravel() for f in files]

    if maskfile is not None:
        maskImg = nibabel.load(maskfile)
        if maskImg.shape != imageDimensions:
            errmsg = 'Mask dimensions {0} not the same as image {1}.'
            raise ValueError(errmsg.format(maskImg.shape, imageDimensions))
        mask = maskImg.get_data().ravel()

    if (scantype == 'SPGR') and (TR is None):
        raise ValueError('SPGR fitting requires TR argument.')

    voisByIndex = {}
## This gets complicated because we don't know if any dimensions are complex instead of spatial
#    if voiCoords is not None:
#        multi_index = tuple([numpy.array(d) for d in voiCoords.T.tolist()])
#        # how many coord dims? this is the number of spatial dims for ravel_index
#        vois = numpy.ravel_multi_index(multi_index, imageDimensions)
#        voisByIndex = {vois[c]:voiCoords[c,:] for c in range(vois.size)}

    affine = anImg.get_affine()
    X = numpy.array(X)
    nx = len(X)
    ny = len(data)
    msg = 'Fitting {0} points with image dimensions {1}.'
    print(msg.format(nx, imageDimensions))
    if not nx == ny:
        msg = 'Number of parameters ({0}) does not match number of images ({1}).'
        raise ValueError(msg.format(nx, ny))

    nvoxels = data[0].size
    t1data = numpy.zeros(data[0].shape)
    start = datetime.now()
    for v in range(nvoxels):
        progress.progressbar(v, nvoxels, start)
        Y = [image[v] for image in data]
        if maskfile is not None:
            if not mask[v]:
                continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if scantype == 'IR':
                    ai = Y[X.argmax()]  # S0
                    bi = 2              # 'z'
                    ci = 1000           # T1
                    p0=[ai, bi, ci]
                    formula = irformula
                    poi = 2
                elif scantype == 'SPGR':
                    ai = Y[X.argmax()]  # S0
                    bi = 1000           # T1
                    p0=[ai, bi]
                    spgrformula.TR = TR
                    formula = spgrformula
                    poi = 1
                else:
                    raise ValueError('Unknown scantype: '+scantype)
                popt, pcov = curve_fit(formula, X, Y, p0=p0)
                t1data[v] = popt[poi]
                if v in voisByIndex:
                    plotFit(formula, popt, X, Y, t1filename, voisByIndex[v])
        except RuntimeError:
            pass
    print(' ')
    t1data = t1data.reshape(imageDimensions)
    t1img = nibabel.Nifti1Image(t1data, affine)
    nibabel.save(t1img, t1filename)
    return t1filename


def plotFit(formula, popt, X, Y, filepath, coords):
    import pdb
    pdb.set_trace()
    filename = os.path.basename(filepath).split('.')[0]
    plotname = '{0}_{1}_fitplot.png'.format(filename, '_'.join(coords))
    plotpath = join(os.path.dirname(filepath), plotname)
    Xrange = numpy.arange(1000)
    fit = [formula(x, *popt) for x in Xrange]
    plt.plot(Xrange, fit) 
    plt.plot(X, Y, 'bo')
    plt.savefig(plotpath)


## zerocrossing
#    lastval = 10000000
#    for x in numpy.arange(0,5000,.1):
#        y = func(x, *popt)
#        if lastval < y:
#            print('zerocrossing: {0}'.format(x))
#            break
#        lastval = y

# todo polarity restoration

#y = S0 (1-V*e pow())

# 80,63,0  1727
# 46,65,0  1113
# 46,30,0   688

# zerocrossing = c * ln(a/b) 
