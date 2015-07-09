from pylabs.utils import Shell


def multiregfilt(images, mat, shell=Shell()):
    cmd = 'regfilt'
    cmd += ' -i {0}'.format(images[0])
    cmd += ' -d {0}'.format(mat)
    shell.run(cmd)
