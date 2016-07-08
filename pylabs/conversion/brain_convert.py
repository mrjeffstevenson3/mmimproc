from pylabs.conversion.parrec2nii_convert import BrainOpts
import pandas as pd
from nipype.interfaces import fsl
from pylabs.conversion.parrec2nii_convert import brain_proc_file
from pylabs.utils.sessions import make_sessions_fm_dict
from cloud.serialization.cloudpickle import dumps
from os.path import join
from datetime import datetime
from collections import defaultdict
from pylabs.utils.paths import getlocaldataroot
fs = getlocaldataroot()
flt = fsl.FLIRT(bins=640, interp='nearestneighbour', cost_func='mutualinfo', output_type='NIFTI')
applyxfm = fsl.ApplyXfm(output_type='NIFTI')

#individual project parameters to be set once here. keys are immutable or code will break.
slu_phant_conv = pd.DataFrame({
            '_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0)},
            '_3D_SPGR_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'verbose': True, 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_fa_{fa}_tr_{tr}_{run}.nii',
                        'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0)},
            '_IR': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'seir', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_tr_{tr}_ti_{ti}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0)},
            })
disc_phant_conv = pd.DataFrame({
            '_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0)},
            '_3D_SPGR_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'verbose': True, 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_fa_{fa}_tr_{tr}_{run}.nii',
                        'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0)},
            '_IR': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'seir', 'scan_info': '', 'fname_template': '{subj}_{scan_name}_tr_{tr}_ti_{ti}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (0)},
            })

self_control_conv = pd.DataFrame({
            '_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{subj}_{session}{scan_name}_{scan_info}_{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3)},
            '_3D_SPGR_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{subj}_{session}{scan_name}_fa_{fa}_tr_{tr}_{run}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3)},
            })

roots_conv = pd.DataFrame({
            '_B1MAP_': {'dirstruct': 'BIDS', 'outdir': 'fmap', 'scan_name': 'b1map', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}{run}.nii',
                        'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_T1_MAP_': {'dirstruct': 'BIDS', 'outdir': 'qt1', 'scan_name': 'spgr', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_fa_{fa}_tr_{tr}_{run}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'fp', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_TOPUP_DTI_32DIR_B1850_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'topup', 'scan_info': '32dir_b1850', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_TOPDN_DTI_31DIR_B1850_': {'dirstruct': 'BIDS', 'outdir': 'dwi', 'scan_name': 'topdn', 'scan_info': '32dir_b1850', 'fname_template': '{subj}_{session}_{scan_name}_{scan_info}_{run}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': True, 'bvs': True, 'dwell_time': True, 'b1corr': False,
                        'field_strength': 3.0, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            '_WE_MEMPRAGE_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'wemempr', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': True},
            '_MEMP_VBM_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': 'vbmmempr', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': False,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': True},
            '_3DT2W_': {'dirstruct': 'BIDS', 'outdir': 'anat', 'scan_name': '3dt2', 'scan_info': '', 'fname_template': '{subj}_{session}_{scan_name}_{run}.nii',
                         'verbose': True, 'compressed': False, 'permit_truncated': False, 'bvs': False, 'dwell_time': False, 'b1corr': True,
                        'field_strength': False, 'vol_info': False, 'origin': 'scanner', 'minmax': ('parse', 'parse'), 'store_header': True,
                        'scaling': 'dv', 'keep_trace': False, 'overwrite': True, 'strict_sort': False, 'multisession': (1, 2, 3), 'rms': False},
            })

#new project DataFrame objects to be added to Panel here
img_conv = pd.Panel({'phantom_qT1_slu': slu_phant_conv,
            'phantom_qT1_disc': disc_phant_conv,
            'self_control': self_control_conv,
            'roots_of_empathy': roots_conv})

opts = BrainOpts()

def set_opts(opt_series): #function to extract params from dataframe
    for index, row in opt_series.iteritems():
        setattr(opts, index, row)

def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.iteritems()}
    return d

def conv_subjs(project, subjects, niftiDict):
    niftiDF = pd.DataFrame()
    if not isinstance(niftiDict, defaultdict):
        raise TypeError('Dictionary not a nested 3 level collections.defaultdict, please fix.')
    if project not in img_conv:
        raise ValueError(project+" not in img_conv Panel. Please check")
    setattr(opts, 'proj', project)
    scans = img_conv[project]
    # loops over subjects for a single project
    for subject in subjects:
        setattr(opts, 'subj', subject)
        for scan in scans:                 #col loop is individual scans
            if all(scans[scan].isnull()) == True:
                continue
            setattr(opts, 'scan', scan)
            set_opts(scans[scan])
            niftiDict = brain_proc_file(opts, niftiDict)
        subjDF = make_sessions_fm_dict(niftiDict, project, subject)
        niftiDF = niftiDF.append(subjDF)
    niftidict = default_to_regular(niftiDict)
    with open(join(fs, project, "niftiDict_all_subj_{:%Y%m%d%H%M}.pickle".format(datetime.now())), "wb") as f:
        f.write(dumps(niftiDict))
    with open(join(fs, project, "niftidict_all_subj_{:%Y%m%d%H%M}.pickle".format(datetime.now())), "wb") as f:
        f.write(dumps(niftidict))
    return niftiDict, niftiDF

def b1corr_anat(project, niftiDict):
    for akey in niftiDict.keys():
        if akey[2] == 'anat':
            for bkey in niftiDict[akey].keys():
                if niftiDict[akey][bkey]['b1corr']:
                    fmap_akey = (akey[0], akey[1], 'fmap')
                    if len(niftiDict[fmap_akey].keys()) != 1:
                        raise ValueError('field map not found or not sure which one to use for '+str(fmap_akey))
                    fmap_bkey = niftiDict[fmap_akey].keys()[0]
                    if not os.path.isfile(niftiDict[fmap_akey][fmap_bkey]['phase_reg2'+niftiDict[akey][bkey]['scan_name']+'_s6_fname']):
                        ref = niftiDict[akey][bkey]['rms_outfilename']
                        outmat_fname = join(niftiDict[fmap_akey][fmap_bkey]['outpath'], fmap_bkey + '_b1mag2' +
                                                   niftiDict[akey][bkey]['scan_name']+'.mat')
                        flt.inputs.in_file = niftiDict[fmap_akey][fmap_bkey]['outfilename']
                        flt.inputs.reference = ref
                        flt.inputs.out_matrix_file = outmat_fname
                        res = flt.run()
                        niftiDict[fmap_akey][fmap_bkey]['b1mag2' + niftiDict[akey][bkey]['scan_name']] = \
                        niftiDict[fmap_akey][fmap_bkey]['outpath'] + '/' + fmap_bkey + '_reg2' + \
                                                   niftiDict[akey][bkey]['scan_name'] + '.mat'
                        phase_fname = join(niftiDict[fmap_akey][fmap_bkey]['outpath'],fmap_bkey + '_phase.nii')
                        cmd = ['fslroi', niftiDict[fmap_akey][fmap_bkey]['outfilename'], phase_fname, 2, 1]
                        subprocess.check_call(cmd, shell=True)
                        niftiDict[fmap_akey][fmap_bkey]['phase_fname'] = phase_fname
                        applyxfm.inputs.in_matrix_file = niftiDict[fmap_akey][fmap_bkey]['matfile2' + niftiDict[akey][bkey]['scan_name']]
                        applyxfm.inputs.in_file = niftiDict[fmap_akey][fmap_bkey]['phase_fname']
                        applyxfm.inputs.out_file = join(niftiDict[fmap_akey][fmap_bkey]['outpath'], fmap_bkey + '_b1phase2' \
                                                          + niftiDict[akey][bkey]['scan_name'] + '.nii')
                        applyxfm.inputs.reference = ref
                        applyxfm.inputs.apply_xfm = True
                        result = applyxfm.run()
                        cmd = 'fslmaths ' + niftiDict[akey][bkey]['outpath'] + '/' + bkey + '_phase_reg2vbmmpr.nii -s 6 '
                        cmd += join(niftiDict[akey][bkey]['outpath'], bkey + '_phase_reg2vbmmpr_s6.nii.gz'
                        subprocess.check_call(cmd, shell=True)
                        niftiDict[akey][bkey]['phase_reg2vbm_s6_fname'] = niftiDict[akey][bkey][
                                                                            'outpath'] + '/' + bkey + '_phase_reg2vbmmpr_s6.nii.gz'
                        niprov.add(niftiDict[akey][bkey]['outpath'] + '/' + bkey + '_phase_reg2vbmmpr_s6.nii.gz')
                    cmd = 'fslmaths ' + niftiDict[k1a][k2v]['rms_fname'] + ' -div ' + niftiDict[akey][bkey][
                        'phase_reg2vbm_s6_fname']
                    cmd += ' -mul 100 ' + niftiDict[k1a][k2v]['outpath'] + '/' + k2v + '_rms_b1corr.nii'
                    subprocess.check_call(cmd, shell=True)
                    niftiDict[k1a][k2v]['b1corr_fname'] = niftiDict[k1a][k2v]['outpath'] + '/' + k2v + '_rms_b1corr.nii.gz'
                    niftiDict = struc_bet(k1a, k2v, 'b1corr_fname', niftiDict)
                    cmd = 'fslmaths ' + niftiDict[k1a][k2w]['rms_fname'] + ' -div ' + niftiDict[akey][bkey][
                        'phase_reg2vbm_s6_fname']
                    cmd += ' -mul 100 ' + niftiDict[k1a][k2w]['outpath'] + '/' + k2w + '_rms_b1corr.nii'
                    subprocess.check_call(cmd, shell=True)
                    niftiDict[k1a][k2w]['b1corr_fname'] = niftiDict[k1a][k2w]['outpath'] + '/' + k2w + '_rms_b1corr.nii.gz'
                    niftiDict = struc_bet(k1a, k2w, 'b1corr_fname', niftiDict)
                    k2t2 = subj + '_ses-' + str(ses) + '_3dt2_' + str(run)
                    if not os.path.isfile(niftiDict[k1a][k2t2]['outfilename']):
                        continue
                    cmd = 'fslmaths ' + niftiDict[k1a][k2t2]['outfilename'] + ' -div ' + niftiDict[akey][bkey][
                        'phase_reg2vbm_s6_fname']
                    cmd += ' -mul 100 ' + niftiDict[k1a][k2t2]['outpath'] + '/' + k2t2 + '_b1corr.nii'
                    subprocess.check_call(cmd, shell=True)
                    niftiDict[k1a][k2t2]['b1corr_fname'] = niftiDict[k1a][k2t2]['outpath'] + '/' + k2t2 + '_b1corr.nii.gz'
                    niftiDict = struc_bet(k1a, k2t2, 'b1corr_fname', niftiDict, frac=0.6)

