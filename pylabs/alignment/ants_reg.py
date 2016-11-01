import subprocess
from os.path import join
from pylabs.utils.provenance import ProvenanceWrapper
from pylabs.utils import run_subprocess
from pylabs.utils import WorkingContext
provenance = ProvenanceWrapper()

def subj2templ_applywarp(moving, ref_img, outfile, warpfiles, execwdir, affine_xform=None, inv=False, args=['--use-NN']):
    if not type(warpfiles) == list:
        raise TypeError('warp file must be a list.')
    if not type(affine_xform) == list:
        raise TypeError('affine file must be a list.')
    cmd = ''
    cmd += 'WarpImageMultiTransform 3 '+moving+' '+outfile+' -R '+ref_img
    cmd += ' '.join(map(str, warpfiles))
    if not affine_xform == None and not inv:
        cmd += ' '.join(map(str, affine_xform))
    elif not affine_xform == None and inv:
        cmd += ' -i '.join(map(str, affine_xform))
    if not args == None:
        cmd += ' '.join(map(str, args))
    with WorkingContext(execwdir):
        subprocess.check_call(cmd, shell=True)
    provenance.log(outfile, 'apply WarpImageMultiTransform', moving, script=__file__)
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
