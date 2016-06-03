import nibabel, os
from nipype.interfaces import fsl
from pylabs.utils import WorkingContext


def skullStrippedMask(targetfpath, provenance, frac=0.5, workingdir='tmpdir'):
    """
    Args:
        workingdir (str): Directory where FSL will run and save intermediate 
                            files, such as brainmask.
    """
    print('Skull stripping..')
    ext = '.nii.gz' if '.gz' in targetfpath else '.nii'
    bet = fsl.BET()
    bet.inputs.in_file = targetfpath
    bet.inputs.frac = frac
    bet.inputs.mask = True
    if not os.path.isdir(workingdir):
        os.mkdir(workingdir)
    with WorkingContext(workingdir):
        result = bet.run() 
    provenance.log(result.outputs.mask_file, 'FSL BET', targetfpath)
    return result.outputs.mask_file

def apply(maskfpath, targetfpath, provenance):
    print('Applying mask..')
    ext = '.nii.gz' if '.gz' in targetfpath else '.nii'
    maskedfpath = targetfpath.replace(ext, '_masked'+ext)
    mask = nibabel.load(maskfpath).get_data()
    img = nibabel.load(targetfpath)
    data = img.get_data()
    assert data.shape == mask.shape
    affine = img.get_affine()
    data[mask==0] = 0
    nibabel.save(nibabel.Nifti1Image(data, affine), maskedfpath)
    provenance.log(maskedfpath, 'brain mask', [targetfpath, maskfpath])
    return maskedfpath
