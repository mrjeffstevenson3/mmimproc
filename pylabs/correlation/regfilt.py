import os
from pylabs.utils import Shell


def multiregfilt(images, mat, shell=Shell()):
    outfiles = []
    for image in images:
        imgname = image.split('.')[0]
        ext = '.'.join(image.split('.')[1:])
        matname = os.path.basename(mat).split('.')[0]
        outfile = '{0}_filt_{1}.{2}'.format(imgname, matname, ext)
        cmd = 'regfilt'
        cmd += ' -i {0}'.format(image)
        cmd += ' -d {0}'.format(mat)
        cmd += ' -f "1"'
        cmd += ' -o {0}'.format(outfile)
        shell.run(cmd)
        outfiles.append(outfile)
    return outfiles
