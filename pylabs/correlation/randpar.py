# Wrappers to invoke FSL's randomise_parallel routine.
from pylabs.utils import Shell


def multirandpar(images, mats, designfile, niterations=500, shell=Shell()):
    """ randomise_parallel on multiple images and/or multiple predictors

    Args:
        images (list): List of image files
        mats (list): List of behavior data .mat files.
        designfile (str): FSL .con file with design.
        niterations (int): Number of iterations to run. Defaults to 500.
        shell (pylabs.utils.Shell): Override to inject a mock for shell calls.
    """
    for image in images:
        for mat in mats:
            outdir = 'randpar_{0}'.format(image.split('.')[0])
            cmd = 'randomize_parallel'
            cmd += ' -i {0}'.format(image)      #input image
            cmd += ' -o {0}/x'.format(outdir)   #output dir
            cmd += ' -d {0}'.format(mat)         #behavior .mat file
            cmd += ' -t {0}'.format(designfile)      #design/ contrast file
            cmd += ' -n {0}'.format(niterations)      #number of iterations
            cmd += ' -T -V'                 #verbose, not sure what T does.
            shell.run(cmd)



