import os, subprocess
from pathlib import *
from os.path import join
import json
import datetime
from pylabs.utils.provenance import ProvenanceWrapper
from pylabs.utils import run_subprocess
from pylabs.utils import WorkingContext
provenance = ProvenanceWrapper()
if not Path(os.environ.get('ANTSPATH'), 'WarpImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpImageMultiTransform in $ANTSPATH directory.')
if not (Path(*Path(os.environ.get('ANTSPATH')).parts[:-2]) / 'ANTs' / 'Scripts' / 'antsRegistrationSyN.sh').is_file():
    raise ValueError('must have ants installed with antsRegistrationSyN.sh in '+str(Path(*Path(os.environ.get('ANTSPATH')).parts[:-2]) / 'ANTs' / 'Scripts')+' directory.')
else:
    antsRegistrationSyN = Path(*Path(os.environ.get('ANTSPATH')).parts[:-2]) / 'ANTs' / 'Scripts' / 'antsRegistrationSyN.sh'


def subj2templ_applywarp(moving, ref_img, outfile, warpfiles, execwdir, affine_xform=None, inv=False, args=['--use-NN']):
    if not type(warpfiles) == list:
        raise TypeError('warpfiles must be a list.')
    if not type(affine_xform) == list:
        raise TypeError('affine_xform must be a list.')
    if not type(args) == list:
        raise TypeError('args must be a list.')
    if inv and (affine_xform == None or not len(warpfiles) == len(affine_xform)):
        raise ValueError('must have affine list with same number of elements when using inverse xfm.')
    cmd = ''
    cmd += 'WarpImageMultiTransform 3 '+moving+' '+outfile+' -R '+ref_img+' '
    if inv:
        cmd += ' '.join(['-i ' + a + ' ' + w for a, w, in zip(reversed(affine_xform), reversed(warpfiles))])+' '
    else:
        cmd += ' '.join([' ' + w for w in map(str, warpfiles)])+' '
        if not affine_xform == None:
            cmd += ' '.join([' '+a for a in map(str, affine_xform)])+' '
    if not args == None:
        cmd += ' '.join([' '+ar for ar in map(str, args)])
    output = ()
    t = datetime.datetime.now()
    output += (str(t),)
    cmdt = (cmd,)
    output += cmdt
    with WorkingContext(execwdir):
        print(cmd)
        output += run_subprocess(cmd)
        with open('applywarp_log.json', mode='a') as logf:
            json.dump(output, logf, indent=2)
    params = {}
    params['warpfiles'] = warpfiles
    params['affine_xform'] = affine_xform
    params['args'] = args
    params['cmd'] = cmd
    params['output'] = output
    params['ref_img'] = ref_img
    provenance.log(outfile, 'apply WarpImageMultiTransform', moving, script=__file__, provenance=params)
    return

def subj2T1(moving, ref_img, outfile, inargs=None):
    if inargs == None or '-n' not in inargs:
        args = ['-n 10', '-t s']
    else:
        args = []
        args = args.append(inargs)
    cmd = ''
    cmd += antsRegistrationSyN + ' -d 3 -f '+ref_img+' -m '+moving
    cmd += ' -o '+outfile+' '
    cmd += ' '.join(map(str, args))
    output = ()
    t = datetime.datetime.now()
    output += (str(t),)
    cmdt = (cmd,)
    output += cmdt
    output += run_subprocess(cmd)
    params = {}
    params['args'] = args
    params['cmd'] = cmd
    params['output'] = output
    params['ref_img'] = ref_img
    provenance.log(outfile, 'antsRegistrationSyN', moving, script=__file__, provenance=params)
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
    params['output'] = output
    params['ref_img'] = ref_img
    with WorkingContext(execwdir):
        output += run_subprocess(cmd)
    provenance.log(join(execwdir, fslmatfilename.replace('.mat', '.txt')),
                   'used c3d_affine_tool to convert fsl .mat file to itk affine',
                   join(execwdir, fslmatfilename), script=__file__, provenance=params)
    return
