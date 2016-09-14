import subprocess
from pylabs.utils.provenance import ProvenanceWrapper
from pylabs.utils import run_subprocess
from pylabs.utils import WorkingContext
provenance = ProvenanceWrapper()

def subj2templ_applywarp(moving, ref_img, outfile, warpfiles, execwdir, affine_xform=None, args=None):
    cmd = ''
    cmd += 'WarpImageMultiTransform 3 '+moving+' '+outfile+' -R '+ref_img+' --use-NN '
    cmd += ' '.join(map(str, warpfiles))+' '
    if not affine_xform == None:
        cmd += affine_xform+' '
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

