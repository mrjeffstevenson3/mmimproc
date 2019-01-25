from os.path import join


def qt1filepath(image, projectdir, dirstruct):
    if dirstruct == 'legacy':
        outdir = join(projectdir, 'T1_{method}_TR{TRtag}'.format(**image))
    elif dirstruct == 'BIDS':
        outdir = join(projectdir, 'sub-phant{0}'.format(image['date']), 'anat')
    else:
        raise ValueError('Unknown directory structure: '+str(dirstruct))
    fnametem = 'sub-phant{date}_T1_{method}_{X}_TR{TRtag}_{run}{b1tag}.nii.gz'
    return join(outdir, fnametem.format(**image))

def filenaming(image, projectdir, names):
    #names is dict of dir and file name format instructions
    if names.dirstruct == 'legacy':
        outdir = join(projectdir, 'T1_{method}_TR{TRtag}'.format(**image))
    elif names.dirstruct == 'BIDS':
        outdir = join(projectdir, names, 'sub-phant{0}'.format(image['date']), 'anat')
    else:
        raise ValueError('Unknown directory structure: '+str(dirstruct))
    fnametem = 'sub-phant{date}_T1_{method}_{X}_TR{TRtag}_{run}{b1tag}.nii.gz'
    return join(outdir, fnametem.format(**image))
