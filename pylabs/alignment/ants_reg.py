import subprocess

def subj2templ_applywarp(moving. ref_img, outfile, warpfiles, affine_xform, args=None):
    cmd = ''
    cmd += 'WarpImageMultiTransform '+moving+' -R '+ref_img+' --use-NN '
    cmd += ' '.join(map(str, warpfiles))+' '
    cmd += affine_xform
    if not args == None:
        cmd += ' '.join(map(str, args))
    subprocess.check_call(cmd, shell=True)
