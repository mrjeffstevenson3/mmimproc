import subprocess
from os.path import join
import json
import datetime
from pylabs.utils.provenance import ProvenanceWrapper
from pylabs.utils import run_subprocess
from pylabs.utils import WorkingContext
provenance = ProvenanceWrapper()

def subj2templ_applywarp(moving, ref_img, outfile, warpfiles, execwdir, affine_xform=None, inv=False, args=['--use-NN']):
    if not type(warpfiles) == list:
        raise TypeError('warpfiles must be a list.')
    if not type(affine_xform) == list:
        raise TypeError('affine_xform must be a list.')
    if not type(args) == list:
        raise TypeError('args must be a list.')
    if inv and affine_xform == None:
        raise ValueError('must have affine list when using inverse xfm.')
    cmd = ''
    cmd += 'WarpImageMultiTransform 3 '+moving+' '+outfile+' -R '+ref_img
    if inv:
        cmd += ' '.join([' -i ' + a for a in map(str, affine_xform)])
        cmd += ' '.join([' ' + w for w in map(str, warpfiles)])
    else:
        cmd += ' '.join([' ' + w for w in map(str, warpfiles)])
        if not affine_xform == None:
            cmd += ' '.join([' '+a for a in map(str, affine_xform)])
    if not args == None:
        cmd += ' '.join([' '+a for a in map(str, args)])
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
    cmd += 'antsRegistrationSyN.sh -d 3 -f '+ref_img+' -m '+moving
    cmd += ' -o '+outfile+' '
    cmd += ' '.join(map(str, args))
    subprocess.check_call(cmd, shell=True)
    provenance.log(outfile, 'antsRegistrationSyN', moving, script=__file__)
    return

def fsl2ants_affine(execwdir, ref, src, fslmatfilename):
    cmd = ''
    cmd += 'c3d_affine_tool -ref '+ref+' -src '+src+' '+fslmatfilename+' -fsl2ras -oitk '
    cmd += fslmatfilename.replace('.mat', '.txt')
    with WorkingContext(execwdir):
        subprocess.check_call(cmd, shell=True)
    provenance.log(join(execwdir, fslmatfilename.replace('.mat', '.txt')),
                   'used c3d_affine_tool to convert fsl .mat file to itk affine',
                   join(execwdir, fslmatfilename), script=__file__)
    return
