from __future__ import division
from os.path import join
import numpy, nibabel, scipy.stats, math, datetime
from numpy import square, sqrt
from mmimproc.utils import progress
from mmimproc.clustering import clusterminsize, cols
import mmimproc.io.images
from pathlib import *
import pandas as pd
import numpy as np
from scipy.stats import spearmanr as sp_correl
from mmimproc.utils.paths import getnetworkdataroot
from mmimproc.utils.provenance import ProvenanceWrapper
from mmimproc.io.images import loadStack
from mmimproc.projects.bbc.pairing import FA_foster_pnames, FA_control_pnames, \
    MD_foster_pnames, MD_control_pnames, RD_foster_pnames, RD_control_pnames, \
    AD_foster_pnames, AD_control_pnames, GMVBM_foster_pnames, GMVBM_control_pnames, WMVBM_foster_pnames, \
    WMVBM_control_pnames, foster_behav_data, control_behav_data
provenance = ProvenanceWrapper()
fs = mmimproc.fs

# function to estimate correlation
def corr(X, Y):
    n = Y.shape[0]
    mx = X.mean(axis=0, keepdims=True)
    my = Y.mean(axis=0, keepdims=True)
    xm, ym = X-mx, Y-my                             #48ms
    r_num = (xm * ym).mean(axis=0)                  #167ms
    r_den = X.std(axis=0) * Y.std(axis=0)           #108ms
    r = r_num / r_den
    t = r * sqrt( (n - 2) / (1 - square(r)) )       #19ms
    return (r, t)


project = 'bbc'
run = 7
niterations = 1000    # for FDR
pcorr_thr = 0.05      # for FDR
cluster_minsize = 12  # for clustering -uses FDR pcorr from that behav and modality for threshold

# ordering is alphanum within pnames, otherwise it would be arbitrary.
foster_files = [FA_foster_pnames, MD_foster_pnames, RD_foster_pnames, AD_foster_pnames, GMVBM_foster_pnames, WMVBM_foster_pnames]
control_files = [FA_control_pnames, MD_control_pnames, RD_control_pnames, AD_control_pnames, GMVBM_control_pnames, WMVBM_control_pnames]

results_dirname = 'py_correl_cthr{clu}_n{n}_run{run}'.format(run=run, clu=cluster_minsize, n=niterations)
results_dir = fs / project / 'stats' / results_dirname
if not results_dir.is_dir():
    results_dir.mkdir(parents=True)
out_pickle_fname = results_dir/"cluster_outfile_{:%Y%m%d%H%M}.pickle".format(datetime.datetime.now())
cluster_report_fname = 'cluster_report.csv' # should be same as in clustering fn
with open(str(results_dir / cluster_report_fname), mode='a') as f:
    f.write('cluster-index,'+','.join(cols)+'\n')   #write cluster header to file

for pool in ['foster', 'control']:
    if pool == 'foster':
        file_list = foster_files
        variables = foster_behav_data
    if pool == 'control':
        file_list = control_files
        variables = control_behav_data

    for files in file_list:
        if (files[0].parts)[-2] == 'WM' or (files[0].parts)[-2] == 'GM':
            mod = (files[0].parts)[-2]
        else:
            mod = (files[0].parts)[-3]
        assert len(files) == variables.shape[0]
        n = nsubjects = variables.shape[0]
        nvars = variables.shape[1]
        data, affine = mmimproc.io.images.loadStack(files)

        spatialdims = data.shape[1:]
        nvoxels = numpy.prod(spatialdims)
        data2d = data.reshape((nsubjects, nvoxels))
        mask1d = (data2d>0).all(axis=0)
        mdata2d = data2d[:, mask1d]
        nvalid = mask1d.sum()
        print('{0:.1f}% of voxels in mask.'.format(nvalid/nvoxels*100))

        X = mdata2d[:, numpy.newaxis, :]
        Y = variables.values[:, :, numpy.newaxis]
        r, t = corr(X, Y)
        p = scipy.stats.t.sf(numpy.abs(t), n - 2) * 2  # 997ms

        nvoxelsScalar = 4
        scalarResults = numpy.zeros((nvars, nvoxelsScalar))
        for v, varname in enumerate(variables.columns.values):
            for k in range(nvoxelsScalar):
                x = mdata2d[:, k]
                y = variables[varname]
                scalarResults[v, k] = scipy.stats.pearsonr(x, y)[0]
        print('Starting FDR permutations..')
        npermutations = math.factorial(n)
        # assert niterations < npermutations
        nbins = 1000
        tmax = 20.
        tres = tmax / nbins
        binedges = numpy.arange(0, tmax - tres, tres)
        tdist = numpy.zeros(binedges.size - 1, dtype=int)
        start = datetime.datetime.now()
        for j in range(niterations):
            progress.progressbar(j, niterations, start)
            I = numpy.random.permutation(numpy.arange(nsubjects))
            Y = variables.values[:, :, numpy.newaxis]
            _, tp = corr(X, Y)
            tdist += numpy.histogram(numpy.abs(tp), binedges)[0]
        alpha = .05
        q = .05
        cumtdist = numpy.cumsum(tdist[::-1]) / tdist.sum()
        closestbin = numpy.abs(cumtdist - (q * alpha)).argmin()
        tcorr = binedges[::-1][closestbin]
        pcorr = scipy.stats.t.sf(tcorr, n - 2)
        assert pcorr < alpha
        print('\nCorrected p-value: {}'.format(pcorr))
        print('Corresponding t-value: {}'.format(tcorr))
        with open(str(results_dir / 'stats_results.txt'), 'a') as f:
            f.write('Corrected p-value for {pool} {mod}: {pcorr}\n'.format(pcorr=pcorr, mod=mod, pool=pool))
            f.write('Corresponding t-value for {pool} {mod}: {tcorr}\n'.format(tcorr=tcorr, mod=mod, pool=pool))

        tneg = t.copy()
        tpos = t.copy()
        tneg[tneg>0] = 0
        tneg = numpy.abs(tneg)
        tpos[tpos<0] = 0
        stats = {
            'r': r,
            'tneg': tneg,
            'tpos': tpos,
            '1minp': 1-p,
            }

        ftemplates = {stat:pool+'_'+mod+'_{}_'+stat+'.nii.gz' for stat in stats.keys()}
        outfnames = {str(var[1]):{} for var in variables.columns.values}

        for stat, vector in stats.items():
            output2d = numpy.zeros((nvars, nvoxels))
            output2d[:, mask1d] = vector
            output4d = output2d.reshape((nvars,) + spatialdims)
            for v, varname in enumerate(variables.columns.values):
                outfnames[varname[1]][stat] = join(str(results_dir), ftemplates[stat].format(varname[1]))
                img = nibabel.Nifti1Image(output4d[v, :, :, :], affine)
                print('Saving file: {}'.format(ftemplates[stat].format(varname[1])))
                nibabel.save(img, outfnames[varname[1]][stat])

        #now save the all file for the given modality
        data4d = np.moveaxis(data, 0, 3)
        _4D_img = nibabel.Nifti1Image(data4d, affine)
        nibabel.save(_4D_img, str(results_dir / str(pool+'_'+mod+'.nii')))
        statfiles, clutables, clumaps = clusterminsize(outfnames, pcorr, minsize=cluster_minsize)
        # todo: write data to h5 file
        # with open(str(out_pickle_fname), "ab") as f:
        #     f.write(dumps([statfiles, clutables, clumaps, outfnames, pcorr, tcorr]))
