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
if not Path(os.environ.get('ANTSPATH'), 'WarpTimeSeriesImageMultiTransform').is_file():
    raise ValueError('must have ants installed with WarpTimeSeriesImageMultiTransform in $ANTSPATH directory.')
if not (Path(*Path(os.environ.get('ANTSPATH')).parts[:-2]) / 'ANTs' / 'Scripts' / 'antsRegistrationSyN.sh').is_file():
    raise ValueError('must have ants installed with antsRegistrationSyN.sh in '+str(Path(*Path(os.environ.get('ANTSPATH')).parts[:-2]) / 'ANTs' / 'Scripts')+' directory.')
else:
    antsRegistrationSyN = Path(*Path(os.environ.get('ANTSPATH')).parts[:-2]) / 'ANTs' / 'Scripts' / 'antsRegistrationSyN.sh'


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
    cmd += moving+' '+outfile+' -R '+ref_img+' '
    if inv:
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
    args = []
    if inargs == None:
        args += ['-n 10', '-t s']
    else:
        if '-n' not in '\t'.join(inargs):
            args += ['-n 10']
        args.append(inargs)
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
    params['ref_img'] = ref
    with WorkingContext(execwdir):
        output += run_subprocess(cmd)
    provenance.log(join(execwdir, fslmatfilename.replace('.mat', '.txt')),
                   'used c3d_affine_tool to convert fsl .mat file to itk affine',
                   join(execwdir, fslmatfilename), script=__file__, provenance=params)
    return
