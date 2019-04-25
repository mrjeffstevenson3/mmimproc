import os
from mmimproc.utils.provenance import ProvenanceWrapper
from mmimproc.utils import Shell
from mmimproc.correlation.fslmatfile import FslMatFile


def multiregfilt(images, matfile, shell=Shell(), provenance=ProvenanceWrapper()):
    outfiles = []
    mat = FslMatFile(matfile)
    for image in images:
        imgname = image.split('.')[0]
        ext = '.'.join(image.split('.')[1:])
        matname = os.path.basename(matfile).split('.')[0]
        outfile = '{0}_filt_{1}.{2}'.format(imgname, matname, ext)
        cmd = 'fsl_regfilt'
        cmd += ' -i {0}'.format(image)
        cmd += ' -d {0}'.format(matfile)
        if mat.numwaves == 1:
            cmd += ' -f 1'
        if mat.numwaves > 1:
           filterindices = ','.join([str(c) for c in range(1, 1 + mat.numwaves)])
           cmd += ' -f \"{0}\"'.format(filterindices)
        cmd += ' -o {0}'.format(outfile)
        provenance.record(cmd)
        outfiles.append(outfile)
    return outfiles
