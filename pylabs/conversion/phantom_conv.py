
import sys, os, datetime
import itertools
from os.path import join as pathjoin
import fnmatch, collections, datetime, cPickle, cloud
import numpy as np
import scipy.ndimage
from dipy.segment.mask import median_otsu
import nibabel
import nibabel.parrec as pr
import nibabel.nifti1 as nifti1
from nibabel.volumeutils import fname_ext_ul_case
from nibabel.orientations import apply_orientation
from nibabel.orientations import inv_ornt_aff
from nibabel.orientations import io_orientation
from niprov import Context



identity_matrix = np.eye(4)
mni_affine = np.array([[-1, 0, 0, 90], [0, 1, 0, -126], [0, 0, 1, -72], [0, 0, 0, 1]])
psl2ras = np.array([[0., 0., -1., 0.], [-1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 0., 1.]])


def printmessage(msg, indent=0):
    if verbose:
        print("%s%s" % (' ' * indent, msg))

def error(msg, exit_code):
    sys.stderr.write(msg + '\n')
    sys.exit(exit_code)
#defaults
verbose = True
prov = Context()

def phantom_B1_midslice_par2mni(parfile, datadict, outdir=None, exceptions=None, outfilename=None,
                                verbose=True, scaling='dv', minmax=('parse', 'parse'), origin='scanner', overwrite=True):

    prov.add(parfile)
    key, value = [], []
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir)
    outfilename = pathjoin(outdir, outfilename)
    parbasename = os.path.basename(parfile)
    infile = fname_ext_ul_case(parfile)
    pr_img = pr.load(infile, permit_truncated=False, scaling=scaling)
    pr_hdr = pr_img.header
    flipangle = int(pr_hdr.__getattribute__('image_defs')[0][29])
    ti = int(round(pr_hdr.__getattribute__('image_defs')[0][34], -1))
    tr = pr_hdr.__getattribute__('general_info').get('repetition_time')
    if tr > 100:
        tr = int(round(pr_hdr.__getattribute__('general_info').get('repetition_time'), -1))
    if ti == 0.0:
        contrast = flipangle
    else:
        contrast = ti
    max_slices = int(pr_hdr.__getattribute__('general_info').get('max_slices'))
    mid_slice_num = int(max_slices) / 2
    scandate = pr_hdr.__getattribute__('general_info').get('exam_date').split('/')[0].strip().replace(".","")

    xdim, ydim, zdim, tdim = [i for i in iter(pr_hdr._shape)]

    slope, intercept = pr_hdr.get_data_scaling(scaling)
    slope = np.array([1.])
    intercept = np.array([0.])
    in_data = np.array(pr_img.dataobj)
    out_dtype = np.float64
    #moving to RAS space
    ornt = io_orientation(np.diag([-1, 1, 1, 1]).dot(pr_img.affine))
    t_aff = inv_ornt_aff(ornt, pr_img.shape)
    affine = np.dot(pr_img.affine, t_aff)
    in_data_ras = apply_orientation(in_data, affine)

    if in_data_ras.shape[3] == zdim and in_data_ras.shape[2] == tdim:
        in_data_ras = np.rollaxis(in_data_ras, 3, 2)

    in_slice_mag = in_data_ras[:,:,mid_slice_num-1,0]
    in_slice_phase = in_data_ras[:,:,mid_slice_num-1,tdim-1]
    mnizoomfactor = 218/float(ydim)
    slice_mag218 = scipy.ndimage.zoom(in_slice_mag, mnizoomfactor, order=0)
    slice_phase218 = scipy.ndimage.zoom(in_slice_phase, mnizoomfactor, order=0)
    slice_mag_mni = slice_mag218[18:200,:]
    #use dipy and ndimage to create a mask
    slice_mag_mni_masked, slice_mag_mni_mask = median_otsu(slice_mag_mni, 8, 1)
    slice_mag_mni_mask = scipy.ndimage.morphology.binary_dilation(slice_mag_mni_mask, iterations=2)
    slice_mag_mni_mask = scipy.ndimage.morphology.binary_fill_holes(slice_mag_mni_mask)
    slice_phase_raw_mni = slice_phase218[18:200,:]
    slice_phase_mf_mni = scipy.ndimage.filters.median_filter(slice_phase_raw_mni, 6)
    slice_phase_mf_mni = slice_phase_mf_mni * slice_mag_mni_mask

    if scandate not in exceptions:
        slice_phase_mf_mni = np.fliplr(slice_phase_mf_mni)
        slice_mag_mni_masked = np.fliplr(slice_mag_mni_masked)
        slice_mag_mni_mask = np.fliplr(slice_mag_mni_mask)

    mydate = datetime.datetime.strptime(scandate, '%Y%m%d').date()
    mymethod = 'b1map'
    partialkey = (mydate, mymethod+'_phase', tr)
    runkeys = [key for key in datadict.keys() if key[:3] == partialkey]
    for run in range(1,len(runkeys)+1):
        exvalues = datadict[partialkey+(run,)]
        for exvalue in exvalues:
            if contrast == exvalue[1]:
                break;
        else:
            break;   # if you just want the run number  # case 2 key found but value/contrast does not exist eg new file
    else:
        run = len(runkeys) + 1 # need to make new run    case 1, case 3

    slice_mag_mni_mask_nimg = nifti1.Nifti1Image(slice_mag_mni_mask.astype(np.float32), mni_affine)
    nibabel.save(slice_mag_mni_mask_nimg, outfilename+'_mag_mask_'+str(run)+'.nii')

    nimg_p = nifti1.Nifti1Image(slice_phase_mf_mni, mni_affine, pr_hdr)
    nhdr_p = nimg_p.header
    nhdr_p.set_data_dtype(out_dtype)
    nhdr_p.set_slope_inter(slope, intercept)
    with open(infile, 'r') as fobj:
        hdr_dump = fobj.read()
        dump_ext = nifti1.Nifti1Extension('comment', hdr_dump)
    nhdr_p.extensions.append(dump_ext)

    nhdr_p['cal_min'] = 0
    nhdr_p['cal_max'] = 200

    nibabel.save(nimg_p, outfilename+'_phase_'+str(run)+'.nii')
    prov.log(outfilename+'_phase_'+str(run)+'.nii', 'median filter 1sl mni b1 phase', parfile)

    nimg_m = nifti1.Nifti1Image(slice_mag_mni_masked, mni_affine, pr_hdr)
    nhdr_m = nimg_m.header
    nhdr_m.set_data_dtype(out_dtype)
    nhdr_m.set_slope_inter(slope, intercept)
    with open(infile, 'r') as fobj:
        hdr_dump = fobj.read()
        dump_ext = nifti1.Nifti1Extension('comment', hdr_dump)
    nhdr_m.extensions.append(dump_ext)

    if 'parse' in minmax:
        # need to get the scaled data
        if verbose:
            printmessage('Loading (and scaling) the data to determine value range')
    if minmax[0] == 'parse':
        nhdr_m['cal_min'] = in_data.min() * slope + intercept
    else:
        nhdr_m['cal_min'] = float(minmax[0])
    if minmax[1] == 'parse':
        nhdr_m['cal_max'] = in_data.max() * slope + intercept
    else:
        nhdr_m['cal_max'] = float(minmax[1])
    nibabel.save(nimg_m, outfilename+'_mag_'+str(run)+'.nii')

    prov.log(outfilename+'_mag_'+str(run)+'.nii', '1sl mni b1 mag', parfile)

    key = [(mydate, mymethod+'_phase', tr, run), (mydate, mymethod+'_mag', tr, run), (mydate, mymethod+'_mag_mask', tr, run)]  # case 3 = found key value pair exists we have repeat run   # case 1 = no key exists eg new file/run for loop never runs
    value = [(outfilename+'_phase_'+str(run)+'.nii', 'phase'), (outfilename+'_mag_'+str(run)+'.nii', 'magnitude'), (outfilename+'_mag_mask_'+str(run)+'.nii', 'mask')]

    if verbose:
        print key, value
    return key, value

def phantom_midslice_par2mni(parfile, datadict, method, outdir=None, exceptions=None, outfilename=None,
                                verbose=True, scaling='fp', minmax=('parse', 'parse'), origin='scanner', overwrite=True):
    prov.add(parfile)
    key, value = [''], ['']
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir)
    outfilename = pathjoin(outdir, outfilename)
    infile = fname_ext_ul_case(parfile)
    pr_img = pr.load(infile, permit_truncated=False, scaling=scaling)
    pr_hdr = pr_img.header
    flipangle = int(pr_hdr.__getattribute__('image_defs')[0][29])
    ti = int(round(pr_hdr.__getattribute__('image_defs')[0][34], -1))
    tr = pr_hdr.__getattribute__('general_info').get('repetition_time')
    if tr > 100:
        tr = int(round(pr_hdr.__getattribute__('general_info').get('repetition_time'), -1))
    if ti == 0.0:
        contrast = flipangle
        outfilename += '_fa_'+str(flipangle).zfill(2)
    else:
        contrast = ti
        outfilename += '_ti_'+str(ti).zfill(4)
    max_slices = int(pr_hdr.__getattribute__('general_info').get('max_slices'))
    scandate = pr_hdr.__getattribute__('general_info').get('exam_date').split('/')[0].strip().replace(".","")
    slope, intercept = pr_hdr.get_data_scaling(scaling)
    slope = np.array([1.])
    intercept = np.array([0.])
    in_data = np.array(pr_img.dataobj)
    out_dtype = np.float64

    if max_slices > 1:
        mid_slice_num = int(max_slices) / 2
    elif max_slices == 1:
        mid_slice_num = 1

    if method == 'orig_spgr' and len(pr_hdr._shape) == 3:
        in_data = np.expand_dims(in_data, 3)
        xdim, ydim, zdim, tdim = [i for i in itertools.chain(iter(pr_hdr._shape), [1])]
    if len(pr_hdr._shape) == 4:
        xdim, ydim, zdim, tdim = [i for i in iter(pr_hdr._shape)]
    #moving to RAS space
    ornt = io_orientation(np.diag([-1, 1, 1, 1]).dot(pr_img.affine))
    t_aff = inv_ornt_aff(ornt, pr_img.shape)
    affine = np.dot(pr_img.affine, t_aff)
    in_data_ras = apply_orientation(in_data, affine)

    if in_data_ras.shape[3] == zdim and in_data_ras.shape[2] == tdim:
        in_data_ras = np.rollaxis(in_data_ras, 3, 2)

    in_slice_mag = in_data_ras[:,:, mid_slice_num-1, 0]
    mnizoomfactor = 218/float(ydim)
    slice_mag218 = scipy.ndimage.zoom(in_slice_mag, mnizoomfactor, order=0)
    slice_mag_mni = slice_mag218[18:200,:]

    if scandate not in exceptions:
        slice_mag_mni = np.fliplr(slice_mag_mni)

    mydate = datetime.datetime.strptime(scandate, '%Y%m%d').date()
    mymethod = method+'_mag'
    partialkey = (mydate, mymethod, tr)
    runkeys = [key for key in datadict.keys() if key[:3] == partialkey]
    for run in range(1,len(runkeys)+1):
        exvalues = datadict[partialkey+(run,)]
        for exvalue in exvalues:
            if contrast == exvalue[1]:
                break;
        else:
            break;   # if you just want the run number  # case 2 key found but value/contrast does not exist eg new file
    else:
        run = len(runkeys) + 1 # need to make new run    case 1, case 3

    nimg_m = nifti1.Nifti1Image(slice_mag_mni, mni_affine, pr_hdr)
    nhdr_m = nimg_m.header
    nhdr_m.set_data_dtype(out_dtype)
    nhdr_m.set_slope_inter(slope, intercept)
    with open(infile, 'r') as fobj:
        hdr_dump = fobj.read()
        dump_ext = nifti1.Nifti1Extension('comment', hdr_dump)
    nhdr_m.extensions.append(dump_ext)

    if 'parse' in minmax:
        # need to get the scaled data
        if verbose == True:
            printmessage('Loading (and scaling) the data to determine value range')
    if minmax[0] == 'parse':
        nhdr_m['cal_min'] = in_data.min() * slope + intercept
    else:
        nhdr_m['cal_min'] = float(minmax[0])
    if minmax[1] == 'parse':
        nhdr_m['cal_max'] = in_data.max() * slope + intercept
    else:
        nhdr_m['cal_max'] = float(minmax[1])
    nibabel.save(nimg_m, outfilename+'_mag_1slmni_'+str(run)+'.nii')
    prov.log(outfilename+'_mag_1slmni_'+str(run)+'.nii', 'magnitude of '+outfilename, parfile)


    if len(pr_hdr._shape) == 4 and pr_hdr._shape[3] == 2 and method != 'orig_spgr':
        in_slice_real = in_data_ras[:,:, mid_slice_num-1,1]
        slice_real218 = scipy.ndimage.zoom(in_slice_real, mnizoomfactor, order=0)
        slice_real_mni = slice_real218[18:200,:]
        if scandate not in exceptions:
            slice_real_mni = np.fliplr(slice_real_mni)

        mydate = datetime.datetime.strptime(scandate, '%Y%m%d').date()
        mymethod = method+'_real'
        partialkey = (mydate, mymethod, tr)

        runkeys = [key for key in datadict.keys() if key[:3] == partialkey]
        for run in range(1,len(runkeys)+1):
            exvalues = datadict[partialkey+(run,)]
            for exvalue in exvalues:
                if contrast == exvalue[1]:
                    break;
            else:
                break;   # if you just want the run number  # case 2 key found but value/contrast does not exist eg new file
        else:
            run = len(runkeys) + 1 # need to make new run    case 1, case 3

        nimg_r = nifti1.Nifti1Image(slice_real_mni, mni_affine, pr_hdr)
        nhdr_r = nimg_r.header
        nhdr_r.set_data_dtype(out_dtype)
        nhdr_r.set_slope_inter(slope, intercept)
        with open(infile, 'r') as fobj:
            hdr_dump = fobj.read()
            dump_ext = nifti1.Nifti1Extension('comment', hdr_dump)
        nhdr_r.extensions.append(dump_ext)
        if 'parse' in minmax:
            # need to get the scaled data
            if verbose == True:
                printmessage('Loading (and scaling) the data to determine value range')
        if minmax[0] == 'parse':
            nhdr_r['cal_min'] = in_data.min() * slope + intercept
        else:
            nhdr_r['cal_min'] = float(minmax[0])
        if minmax[1] == 'parse':
            nhdr_r['cal_max'] = in_data.max() * slope + intercept
        else:
            nhdr_r['cal_max'] = float(minmax[1])
        nibabel.save(nimg_r, outfilename+'_real_1slmni_'+str(run)+'.nii')
        prov.log(outfilename+'_real_1slmni_'+str(run)+'.nii', 'real component of '+outfilename, parfile,)

        key = [(mydate, method+'_mag', tr, run), (mydate, mymethod, tr, run),]
        value = [(outfilename+'_mag_1slmni_'+str(run)+'.nii', contrast), (outfilename+'_real_1slmni_'+str(run)+'.nii', contrast),]

    else:
        key = [(mydate, mymethod, tr, run)]
        value = [(outfilename+'_mag_1slmni_'+str(run)+'.nii', contrast)]

    if verbose:
        print key, value
    return key, value


