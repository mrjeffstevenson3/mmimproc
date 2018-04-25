# todo: fssurf2subj and fslabel2subj
import os, subprocess
from pathlib import *
from os.path import join
import json
import datetime
from pylabs.utils import *
provenance = ProvenanceWrapper()

regd = { # first key is reg_fn called inside antsreg function
        'regspgrs2fa05': { # file names, fa, tr
            'inftempl': 'img_conv[\'%(project)s\'][\'_T1_MAP_\'][\'fname_template\']'}
        }

def antsreg(project, reg_fn, subjects, args=['-n 12'] ,quick=False):
    # make antscmd_spgr to reg list of spgr to 1 ref.
    antsRegistrationSyN = get_antsregsyn_cmd(quick)
    spgr_fntempl = eval(regd[reg_fn]['inftempl'] % {'project': project})

    return spgr_fntempl, antsRegistrationSyN


def subj2templ_applywarp(moving, ref_img, outfile, warpfiles, execwdir, dims=3, affine_xform=None, inv=False, args=['--use-NN']):
    if not type(warpfiles) == list:
        raise TypeError('warpfiles must be a list.')
    if not type(affine_xform) == list:
        raise TypeError('affine_xform must be a list.')
    if not type(args) == list:
        raise TypeError('args must be a list.')
    if not len(warpfiles) == len(affine_xform) and not affine_xform == None:
        raise ValueError('must have affine list with same number of elements as warpfiles list.')
    if dims > 4 or dims < 2:
        raise ValueError('dims must be between 2 and 4. Default: dims=3.')
    cmd = ''
    if dims == 4:
        cmd += 'WarpTimeSeriesImageMultiTransform 4 '
    if dims == 3 or dims == 2:
        cmd += 'WarpImageMultiTransform '+str(dims)+' '
    cmd += str(moving)+' '+str(outfile)+' -R '+str(ref_img)+' '
    if inv:
        print "inverse selected, reversing order of ants Warp and affine list for "+outfile
        cmd += ' '.join(['-i ' + a + ' ' + w for a, w in zip(reversed(affine_xform), reversed(warpfiles))])+' '
    elif not affine_xform == None:
        cmd += ' '.join([w + ' ' + a for a, w in zip(affine_xform, warpfiles)])+' '
    else:
        cmd += ' '.join([w for w in map(str, warpfiles)])+' '
    if not args == None:
        cmd += ' '.join([' '+ar for ar in map(str, args)])
    output = ()
    t = datetime.datetime.now()
    output += (str(t),)
    output += (cmd,)
    with WorkingContext(execwdir):
        print(cmd)
        output += run_subprocess(cmd)
        with open('applywarp_log.json', mode='a') as logf:
            json.dump(output, logf, indent=2)
    params = {}
    params['warpfiles'] = warpfiles
    params['affine_xform'] = affine_xform
    params['inverse'] = inv
    params['args'] = args
    params['cmd'] = cmd
    params['output'] = output
    params['ref_img'] = ref_img
    provenance.log(outfile, 'apply WarpImageMultiTransform', moving, script=__file__, provenance=params)
    return tuple([(k, v) for k, v in params.iteritems()])

def subj2T1(moving, ref_img, outfile, inargs=None):
    """

    :param moving:
    :param ref_img:
    :param outfile:
    :param inargs: input arguments -n <num cpu>
    :example inargs:  -n 30 -t s -p f -j 1 -s 10 -r 1
    :return:
    """
    antsRegistrationSyN = get_antsregsyn_cmd()
    args = []
    if inargs == None:
        args += ['-n 10', '-t s']
    else:
        if '-n' not in '\t'.join(inargs):
            args += ['-n 10']
        args.append(inargs)
    cmd = str(antsRegistrationSyN) + ' -d 3 -f ' + str(ref_img) + ' -m ' + str(moving) + ' -o ' + str(outfile)
    cmd += ' ' + ' '.join(map(str, args))
    output = ()
    t = datetime.datetime.now()
    output += (str(t),)
    output += (cmd,)
    output += run_subprocess(cmd)
    params = {}
    params['args'] = args
    params['cmd'] = cmd
    params['output'] = output
    params['ref_img'] = ref_img
    provenance.log(str(outfile), 'antsRegistrationSyN', str(moving), script=__file__, provenance=params)
    return

def fsl2ants_affine(execwdir, ref, src, fslmatfilename):
    cmd = ''
    cmd += 'c3d_affine_tool -ref '+ref+' -src '+src+' '+fslmatfilename+' -fsl2ras -oitk '
    cmd += fslmatfilename.replace('.mat', '.txt')
    output = ()
    t = datetime.datetime.now()
    output += (str(t),)
    cmdt = (cmd,)
    output += cmdt
    params = {}
    params['cmd'] = cmd
    params['ref_img'] = ref
    with WorkingContext(execwdir):
        output += run_subprocess(cmd)
    params['output'] = output
    provenance.log(join(execwdir, fslmatfilename.replace('.mat', '.txt')),
                   'used c3d_affine_tool to convert fsl .mat file to itk affine',
                   join(execwdir, fslmatfilename), script=__file__, provenance=params)
    return

def fs_lta2fsl_mat(execwdir, mov, ref, fs_lta_fname):
    if not Path(fs_lta_fname).is_file():
        raise ValueError('fslta_fname file must exist or cannot be found. ' + fs_lta_fname)
    if not Path(mov).is_file():
        raise ValueError('mov file must exist or cannot be found. ' + mov)
    if not Path(ref).is_file():
        raise ValueError('ref file must exist or cannot be found. ' + ref)
    if not Path(execwdir).is_dir():
        raise ValueError('execwdir directory must exist. ' + execwdir)
    #set up command
    cmd = 'lta_convert --inlta '+ fs_lta_fname
    cmd += ' --outfsl '+fs_lta_fname.replace('.lta', '.mat')
    cmd += ' --src '+mov+' --trg '+ref
    #set up
    output = ()
    t = datetime.datetime.now()
    output += (str(t),)
    cmdt = (cmd,)
    output += cmdt
    params = {}
    params['cmd'] = cmd
    params['ref_img'] = ref
    with WorkingContext(execwdir):
        output += run_subprocess(cmd)
    params['output'] = output
    provenance.log(fs_lta_fname.replace('.lta', '.mat'),
                   'used freesurfer lta_convert to convert .lta xform to fsl .mat affine file',
                   fs_lta_fname, script=__file__, provenance=params)
    return

def fsl_mat2fs_lta(execwdir, mov, ref, fslmat_fname):
    if not Path(fslmat_fname).is_file():
        raise ValueError('fslta_fname file must exist or cannot be found. ' + fslmat_fname)
    if not Path(mov).is_file():
        raise ValueError('mov file must exist or cannot be found. ' + mov)
    if not Path(ref).is_file():
        raise ValueError('ref file must exist or cannot be found. ' + ref)
    if not Path(execwdir).is_dir():
        raise ValueError('execwdir directory must exist. ' + execwdir)
    #set up command
    cmd = 'lta_convert --infsl '+ fslmat_fname
    cmd += ' --outlta '+fslmat_fname.replace('.mat', '.lta')
    cmd += ' --src '+mov+' --trg '+ref
    #set up
    output = ()
    t = datetime.datetime.now()
    output += (str(t),)
    cmdt = (cmd,)
    output += cmdt
    params = {}
    params['cmd'] = cmd
    params['ref_img'] = ref
    with WorkingContext(execwdir):
        output += run_subprocess(cmd)
    params['output'] = output
    provenance.log(fslmat_fname.replace('.mat', '.lta'),
                   'used freesurfer lta_convert to convert .lta xform to fsl .mat affine file',
                   fslmat_fname, script=__file__, provenance=params)
    return



def fsvol2subj(moving, ref_img, outfile, subj_path, xform={'regheader': True}, convert2nii=True, args=[]):
    """
    mri_vol2vol - -mov brain.mgz - -targ rawavg.mgz - -regheader - -o
    brain - in -rawavg.mgz - -no-save-reg
    """
    cmd = ''
    #ref vol
    #if Path(ref_img).is_file():
        #applyreg.inputs.target_file = ref_img
    #else:
        #raise ValueError('ref_img file must exist or cannot be found. ' + ref_img)
    #test which transform to use via xform dict parameter
    if 'regheader' in xform and xform['regheader'] == True:
        cmd += ' --regheader '
    if 'reg_file' in xform and Path(xform['reg_file']).is_file():
        cmd += ' --reg '+ xform['reg_file']
    if 'fsl_reg_file' in xform and Path(xform['fsl_reg_file']).is_file():
        cmd += ' --fsl '+xform['fsl_reg_file']
    if not Path(moving).is_file():
        raise ValueError('moving file must exist or cannot be found. '+moving)

    output = ()
    t = datetime.datetime.now()
    output += (str(t),)
    cmdt = (cmd,)
    output += cmdt
    params = {}
    params['cmd'] = cmd
    params['output'] = output
    params['ref_img'] = ref_img


    provenance.log(outfile, 'apply WarpImageMultiTransform', moving, script=__file__, provenance=params)
    if convert2nii:
        output += run_subprocess('mri_convert '+outfile+' '+ outfile.replace('.mgz', '.nii'))
        params['output'] = output
        provenance.log(outfile.replace('.mgz', '.nii'), 'convert aligned freesurfer vol in subject space to nifti', moving, script=__file__, provenance=params)



def fslabel2subj(moving, ref_img, outfile, subj_path, xform={'regheader': True}, convert2nii=True, args=[]):
    """
    mri_label2vol - -seg aseg.mgz - -temp rawavg.mgz - -o
    aseg - in -rawavg.mgz - -regheader aseg.mgz
    """
    cmd = 'mri_label2vol --seg '

    return




def fssurf2subj():
    return