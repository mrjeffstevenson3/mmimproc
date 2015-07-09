from pylabs.utils import Shell


def multiregfilt(images, mat, shell=Shell()):
    for image in images:
        outfile = '{0[0]}_filt_{1[0]}.{0[1]}'.format(
            image.split('.'), mat.split('.'))
        cmd = 'regfilt'
        cmd += ' -i {0}'.format(image)
        cmd += ' -d {0}'.format(mat)
        cmd += ' -f "1"'
        cmd += ' -o {0}'.format(outfile)
        shell.run(cmd)
