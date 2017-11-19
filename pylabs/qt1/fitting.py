from pathlib import *
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

def t1fit(files, X, TR=None, maskfile=None, b1file=None, scantype='IR', t1filename=None, 
    voiCoords=None, mute=False):

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

    if b1file is not None:
        b1Img = nibabel.load(b1file)
        if b1Img.shape != imageDimensions:
            errmsg = 'B1 map dimensions {0} not the same as image {1}.'
            raise ValueError(errmsg.format(b1Img.shape, imageDimensions))
        B1 = b1Img.get_data().ravel()

    if (scantype == 'SPGR') and (TR is None):
        raise ValueError('SPGR fitting requires TR argument.')

    voisByIndex = {}

    affine = anImg.affine
    X = numpy.array(X)
    if scantype == 'SPGR':
        X = numpy.radians(X)
    nx = len(X)
    ny = len(data)
    msg = 'Fitting {0} points with image dimensions {1}.'
    if not mute:
        print(msg.format(nx, imageDimensions))
    if not nx == ny:
        msg = 'Number of parameters ({0}) does not match number of images ({1}).'
        raise ValueError(msg.format(nx, ny))

    nvoxels = data[0].size
    t1data = numpy.zeros(data[0].shape)
    start = datetime.now()
    for v in range(nvoxels):
        if maskfile is not None:
            if not mask[v]:
                continue
        if not mute:
            progress.progressbar(v, nvoxels, start)
        Y = numpy.array([image[v] for image in data])
        if b1file is not None:
            Xv = X*(B1[v]/100.)
        else:
            Xv = X
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if scantype == 'IR':
                    ai = Y[Xv.argmax()]  # S0
                    bi = 2              # 'z'
                    ci = 1000           # T1
                    p0=[ai, bi, ci]
                    formula = irformula
                    poi = 2
                elif scantype == 'SPGR':
                    ai = 15*Y.max()  # S0
                    bi = 1000           # T1
                    p0=[ai, bi]
                    spgrformula.TR = TR
                    formula = spgrformula
                    poi = 1
                else:
                    raise ValueError('Unknown scantype: '+scantype)
                popt, pcov = curve_fit(formula, Xv, Y, p0=p0)

                t1data[v] = popt[poi]

                if v in voisByIndex:
                    plotFit(formula, popt, Xv, Y, t1filename, voisByIndex[v])
        except RuntimeError:
            pass

    print(' ')
    t1data = t1data.reshape(imageDimensions)
    t1img = nibabel.Nifti1Image(t1data, affine)
    t1img.header.set_qform(affine, code=1)
    t1img.header.set_sform(affine, code=1)
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

# more todo: add linearization options for least sq and linear regression to SPGR multi flip angle
# from jasper:

# from os.path import join
# import glob
# import numpy
# import nibabel
# import matplotlib
# matplotlib.use('TkAgg')
# import matplotlib.pyplot as plt
# import seaborn
# from pylabs.utils import progress
# import datetime
#
# #high T1 116 135      27975
#
# datadir = '/Users/rubi/Data/qt1'
# fafilefilter = 'sub-phant2017-10-19_spgr_fa_*_tr_12p0_1.nii'
# maskfilename = 'sub-phant2017-10-19_spgr_mask.nii'
#
# TR = 12.0
# faFiles = glob.glob(join(datadir, fafilefilter))
# flipAngles = [float(f.split('_')[-4]) for f in faFiles]

# k = 200*240*1 # total nr of voxels
# dims = [200, 240]
# data = numpy.full([len(flipAngles), k], numpy.nan)
# anImg = nibabel.load(faFiles[0])
# for f, fpath in enumerate(faFiles):
#     data[f, :] = nibabel.load(fpath).get_data()[:,:,120].flatten()
#
# t1 = numpy.full([k,], numpy.nan)
# start = datetime.datetime.now()
# for v in range(k):
#
#
#     if v % 10 == 0:
#         progress.progressbar(v, k, start)
#     Sa = data[:, v]
#     a = numpy.radians(flipAngles)
#
#     #a = numpy.tile(numpy.atleast_2d(flipAngles).T, [1, k])
#
#     y = Sa / numpy.sin(a)
#     x = Sa / numpy.tan(a)
#     A = numpy.vstack([x, numpy.ones(len(x))]).T
#     m, c = numpy.linalg.lstsq(A, y)[0]
#     t1[v] = -TR/numpy.log(m)
#
#
#
# t1data = t1.reshape(dims)
# t1img = nibabel.Nifti1Image(t1data, anImg.affine)
# nibabel.save(t1img, 't1.nii')
