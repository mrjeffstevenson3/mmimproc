# Wrappers to invoke FSL's randomise_parallel routine.
from pylabs.utils import Shell


def multirandpar(images, mats, designfile, niterations=50, shell=Shell()):
    """ randomise_parallel on multiple images and/or multiple predictors

    Expects mask files to exist for each unique image prefix 
    (underscore-delineated); i.e. "GM_mod_merge.img" would require a "GM_mask"

    Args:
        images (list): List of image files
        mats (list): List of behavior data .mat files.
        designfile (str): FSL .con file with design.
        niterations (int): Number of iterations to run. Defaults to 50.
        shell (pylabs.utils.Shell): Override to inject a mock for shell calls.
    """
    for image in images:
        maskfile = '{0}_mask'.format(image.split('_')[0])
        outdir = 'randpar_{0}_{1}'.format(niterations, image.split('.')[0])
        shell.run('mkdir -p {0}'.format(outdir))
        for mat in mats:
            outfile = '{0}'.format(mat.split('.')[0])
            cmd = 'randomize_parallel'
            cmd += ' -i {0}'.format(image)                  #input image
            cmd += ' -o {0}/{1}'.format(outdir, outfile)   #output dir, file
            cmd += ' -m {0}'.format(maskfile)               #mask file
            cmd += ' -d {0}'.format(mat)                #behavior .mat file
            cmd += ' -t {0}'.format(designfile)      #design/ contrast file
            cmd += ' -n {0}'.format(niterations)      #number of iterations
            cmd += ' -T -V'                 #verbose, not sure what T does.
            shell.run(cmd)



