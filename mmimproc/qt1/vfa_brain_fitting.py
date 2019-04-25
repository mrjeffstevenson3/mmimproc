
import mmimproc
mmimproc.datadir.target = 'jaba'
from pathlib import *
from mmimproc.utils import *
from mmimproc.io.images import savenii
from scipy import stats
import numpy as np


def vfa_fit_2e2fa(vfa, info_dict, b1map, mask=None):

    # info_dict contains all relevant info for fitting eg. flip angles, trs, file names, paths, etc
    # fit vfa and make b1corrected qt1 img
    vy_vfa2_ec1 = vfa[:,:,:,:2]
    vy_vfa2_ec2 = vfa[:,:,:,2:4]
    vy_vfa2_ec1_rms = np.sqrt(np.sum(np.square(vy_vfa2_ec1), axis=3)/vy_vfa2_ec1.shape[3])
    vy_vfa2_ec2_rms = np.sqrt(np.sum(np.square(vy_vfa2_ec2), axis=3)/vy_vfa2_ec2.shape[3])
    k = np.prod(vy_vfa2_ec1_rms.shape)
    data = np.zeros([len(info_dict['fas']), k])
    data[0,:] = vy_vfa2_ec1_rms.flatten()
    data[1,:] = vy_vfa2_ec2_rms.flatten()
    fa_uncorr = np.zeros(data.shape)
    fa_b1corr = np.zeros(data.shape)
    for i, fa in enumerate(info_dict['fas']):
        fa_uncorr[i, :] = fa
    fa_b1corr = fa_uncorr * b1map.flatten()  # uses broadcasting
    fa_b1corr[fa_b1corr == np.inf] = np.nan
    fa_b1corr_rad = np.radians(fa_b1corr)
    y = data / np.sin(fa_b1corr_rad)
    x = data / np.tan(fa_b1corr_rad)
    m = np.zeros(k)
    if not mask == None:
        mask = mask.astype('bool').flatten()
    for v in range(k):
        if not mask == None:
            if mask[v]:
                m[v], intercept, r, p, std = stats.linregress(x[:, v], y[:, v])
        else:
            m[v], intercept, r, p, std = stats.linregress(x[:, v], y[:, v])
    qT1_linregr = -info_dict['vfa_tr']/np.log(m)
    qT1_linregr_data = qT1_linregr.reshape(vy_vfa2_ec1_rms.shape)
    qT1_linregr_data[qT1_linregr_data < 1.0] = 0
    qT1_linregr_data[qT1_linregr_data > 6000] = 6000
    qT1_linregr_data_clean = np.nan_to_num(qT1_linregr_data, copy=True)
    savenii(qT1_linregr_data_clean, info_dict['affine'], str(info_dict['outfile']))

