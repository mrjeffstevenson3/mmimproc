import subprocess
import niprov

def subj2templ_applywarp(moving, ref_img, outfile, warpfiles, cwd=None, affine_xform=None, args=None):
    cmd = ''
    cmd += 'WarpImageMultiTransform 3 '+moving+' '+outfile+' -R '+ref_img+' --use-NN '
    cmd += ' '.join(map(str, warpfiles))+' '
    if not affine_xform == None:
        cmd += affine_xform+' '
    if not args == None:
        cmd += ' '.join(map(str, args))
    subprocess.check_call(cmd, shell=True)
    niprov.log(outfile, 'apply WarpImageMultiTransform', moving, script=__file__)
    return

def subj2T1(moving, ref_img, outfile, args=['-n 10', '-t s']):
    cmd = ''
    cmd += 'antsRegistrationSyN.sh -d 3 -f '+ref_img+' -m '+moving
    cmd += ' -o '+outfile+' '
    cmd += ' '.join(map(str, args))
    subprocess.check_call(cmd, shell=True)
    niprov.log(outfile, 'antsRegistrationSyN', moving, script=__file__)
    return