# -*- coding: utf-8 -*-
from pathlib import *
import matplotlib.pyplot as plt
import os, warnings
import numpy as np
import nibabel as nib
from scipy.optimize import curve_fit
from numpy import exp, cos, sin
from dipy.segment.mask import median_otsu
from dipy.segment.mask import applymask
from mmimproc.utils import progress, appendposix
from datetime import datetime
from os.path import join
from dipy.align.reslice import reslice
from mmimproc.io.images import savenii
from mmimproc.fmap_correction.b1_map_corr import calcb1map
from scipy import stats
from scipy.ndimage.filters import median_filter as medianf





def irformula(x, a, b, c):
    return np.abs(a * (1 - b * exp(-x/c)))

def spgrformula(x, a, b):
    TR = spgrformula.TR
    return a * ((1-exp(-TR/b))/(1-cos(x)*exp(-TR/b))) * sin(x)

def t1fit(files, X, TR=None, maskfile=None, b1file=None, scantype='IR', t1filename=None, 
    voiCoords=None, mute=False):

    if t1filename is None:
        t1filename = 't1_fit.nii.gz'

    if isinstance(files, basestring):
        anImg = nib.load(files)
        imageDimensions = anImg.shape[:-1]
        data = [anImg.get_data()[...,i].ravel() for i in range(anImg.shape[-1])]
    else:
        anImg = nib.load(files[0])
        imageDimensions = anImg.shape 
        data = [nib.load(f).get_data().ravel() for f in files]

    if maskfile is not None:
        maskImg = nib.load(maskfile)
        if maskImg.shape != imageDimensions:
            errmsg = 'Mask dimensions {0} not the same as image {1}.'
            raise ValueError(errmsg.format(maskImg.shape, imageDimensions))
        mask = maskImg.get_data().ravel()

    if b1file is not None:
        b1Img = nib.load(b1file)
        if b1Img.shape != imageDimensions:
            errmsg = 'B1 map dimensions {0} not the same as image {1}.'
            raise ValueError(errmsg.format(b1Img.shape, imageDimensions))
        B1 = b1Img.get_data().ravel()

    if (scantype == 'SPGR') and (TR is None):
        raise ValueError('SPGR fitting requires TR argument.')

    voisByIndex = {}

    affine = anImg.affine
    X = np.array(X)
    if scantype == 'SPGR':
        X = np.radians(X)
    nx = len(X)
    ny = len(data)
    msg = 'Fitting {0} points with image dimensions {1}.'
    if not mute:
        print(msg.format(nx, imageDimensions))
    if not nx == ny:
        msg = 'Number of parameters ({0}) does not match number of images ({1}).'
        raise ValueError(msg.format(nx, ny))

    nvoxels = data[0].size
    t1data = np.zeros(data[0].shape)
    start = datetime.now()
    for v in range(nvoxels):
        if maskfile is not None:
            if not mask[v]:
                continue
        if not mute:
            progress.progressbar(v, nvoxels, start)
        Y = np.array([image[v] for image in data])
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
    t1img = nib.Nifti1Image(t1data, affine)
    t1img.header.set_qform(affine, code=1)
    t1img.header.set_sform(affine, code=1)
    nib.save(t1img, t1filename)
    return t1filename

def vfa_qt1fit(vfa_data, fas,  b1map, TR, outfile, affine, mask=None):
    """
    Used to fit variable flip angle VY patch qT1 spgr data with B1 correction
    :param vfa_data:  4D spgr multi echo multi flip angle data (2 echos + 2 fa)
    :param fas:       the 2 flip angles used. gotten from protocol. PAR file info wrong!
    :param b1map:     the b1 correction factor as decimal. 1.0=no change.
    :param TR:        the TR of the spgr sequence making vfa_data
    :param outfile:   Posix file name to save qT1. Automatically overwrites!
    :param affine:    Affine for the qT1 nifti file when saving.
    :param mask:      same shape 3D boolian mask to speed up processing, and clean up outfile.
                      mask='make' will create a mask using dipy median_otsu
    :return:          nothing.
    """
    if not vfa_data.shape[:3] == b1map.shape:
        raise ValueError('VFA data and b1map must have same dimensions')
    if mask is not None and not mask == 'make':
        if not mask.shape == b1map.shape:
            raise ValueError('Mask, data, and b1map must have same first 3 dimensions')
    if not vfa_data.shape[3] == 4:
        raise ValueError('VFA data must have 4 vols, 2 echos and 2 flip angles')
    vy_vfa1 = vfa_data[:, :, :, :2]
    vy_vfa2 = vfa_data[:, :, :, 2:4]
    vy_vfa1_rms = np.sqrt(np.sum(np.square(vy_vfa1), axis=3) / vy_vfa1.shape[3])
    vy_vfa2_rms = np.sqrt(np.sum(np.square(vy_vfa2), axis=3) / vy_vfa2.shape[3])
    if mask == 'make':
        vfa2_brain, mask = median_otsu(vy_vfa2_rms, median_radius=2, numpass=1)
    k = np.prod(vy_vfa1_rms.shape)
    data = np.zeros([len(fas), k])
    data[0, :] = vy_vfa1_rms.flatten()
    data[1, :] = vy_vfa2_rms.flatten()
    fa_uncorr = np.zeros(data.shape)
    fa_b1corr = np.zeros(data.shape)
    for i, fa in enumerate(fas):
        fa_uncorr[i, :] = fa
    fa_b1corr = fa_uncorr * b1map.flatten()  # uses broadcasting
    fa_b1corr[fa_b1corr == np.inf] = np.nan
    fa_b1corr_rad = np.radians(fa_b1corr)
    y = data / np.sin(fa_b1corr_rad)
    x = data / np.tan(fa_b1corr_rad)
    m = np.zeros(k)
    if mask is not None or mask == 'make':
        mask = mask.flatten()
        for v in range(k):
            if mask[v]:
                m[v], intercept, r, p, std = stats.linregress(x[:, v], y[:, v])
    else:
        for v in range(k):
            m[v], intercept, r, p, std = stats.linregress(x[:, v], y[:, v])
    qT1_linregr = -TR / np.log(m)
    qT1_linregr_data = qT1_linregr.reshape(vy_vfa1_rms.shape)
    qT1_linregr_data[(qT1_linregr_data < 1) | (qT1_linregr_data == np.nan)] = 0
    qT1_linregr_data[qT1_linregr_data > 6000] = 6000
    if not mask == None:
        qT1_linregr_data = applymask(qT1_linregr_data, mask.reshape(qT1_linregr_data.shape))
    savenii(qT1_linregr_data, affine, str(outfile))
    if mask == 'make':
        savenii(mask.astype('int'), affine, str(appendposix(outfile, '_mask')))
    return

def plotFit(formula, popt, X, Y, filepath, coords):
    import pdb
    pdb.set_trace()
    filename = os.path.basename(filepath).split('.')[0]
    plotname = '{0}_{1}_fitplot.png'.format(filename, '_'.join(coords))
    plotpath = join(os.path.dirname(filepath), plotname)
    Xrange = np.arange(1000)
    fit = [formula(x, *popt) for x in Xrange]
    plt.plot(Xrange, fit) 
    plt.plot(X, Y, 'bo')
    plt.savefig(plotpath)


## zerocrossing
#    lastval = 10000000
#    for x in np.arange(0,5000,.1):
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
# from mmimproc.utils import progress
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
# data = np.full([len(flipAngles), k], np.nan)
# anImg = nib.load(faFiles[0])
# for f, fpath in enumerate(faFiles):
#     data[f, :] = nib.load(fpath).get_data()[:,:,120].flatten()
#
# t1 = np.full([k,], np.nan)
# start = datetime.datetime.now()
# for v in range(k):
#
#
#     if v % 10 == 0:
#         progress.progressbar(v, k, start)
#     Sa = data[:, v]
#     a = np.radians(flipAngles)
#
#     #a = np.tile(np.atleast_2d(flipAngles).T, [1, k])
#
#     y = Sa / np.sin(a)
#     x = Sa / np.tan(a)
#     A = np.vstack([x, np.ones(len(x))]).T
#     m, c = np.linalg.lstsq(A, y)[0]
#     t1[v] = -TR/np.log(m)
#
#
#
# t1data = t1.reshape(dims)
# t1img = nib.Nifti1Image(t1data, anImg.affine)
# nib.save(t1img, 't1.nii')
