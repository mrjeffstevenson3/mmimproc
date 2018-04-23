# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import shutil
import numpy as np
import nibabel as nib
from pylabs.utils import *

def inject_vol_data_into_vtk(working_dir, vol_fname, vtk_infname, vtk_outfname):
    results = (,)
    vtk_infname = Path(vtk_infname)
    vtk_outfname = Path(vtk_outfname)
    shutil.copy(str(vtk_infname), 'f.vtk')
    img = nib.load(str(vol_fname))
    affine = img.affine
    offsets = {'x': affine[0, 3], 'y': affine[1, 3], 'z': affine[2, 3]}
    nib.save(nib.AnalyzeImage(img.get_data().astype('float32'), affine),'stats1.hdr')
    with WorkingContext(working_dir):
        with open('usechannel.txt', 'w') as uc:
            uc.write('1\n')
        with open('procmethod.txt', 'w') as pm:
            pm.write('1\n')
        with open('filesize.txt', 'w') as fsz:
            fsz.write(str(Path(vtk_infname).stat().st_size)+'\n')
        with open('offsets.txt', 'w') as off:
            off.write('{x} {y} {z}\n'.format(**offsets))
        shutil.copy(str(aal_motor), 'aal_motor.vtk')
        shutil.copy(str(aal_base), 'base.vtk')
        shutil.copy(str(aal_channel), 'channel.vtk')
        results += run_subprocess(vol2fiber)
        Path('fnew.vtk').rename(vtk_outfname)
    return

'''
bash script to convert to python:

cd /mnt/users/js/nbwr/sub-nbwr999b/ses-1/Slicer_scenes/Slicer_1st_noddi_run_5-8-2017/toddtest
echo "1" > usechannel.txt
echo "1" > procmethod.txt
FILESIZE=$(stat -c%s "f.vtk")
echo $FILESIZE > filesize.txt
cp sub-nbwr999b_ses-1_qT1_b1corr_clamped_reg2dwi_Warped.nii.gz stats.nii.gz
fslhd -x stats > S0_hdr.txt

grep sto_ijk S0_hdr.txt > z.txt
xoffset=`cat z.txt | awk '{ print $7 }'`
yoffset=`cat z.txt | awk '{ print $11 }'`
zoffset=`cat z.txt | awk '{ print $15 }'`
echo $xoffset $yoffset $zoffset > offsets.txt
rm stats1*
cp stats.nii.gz stats1.nii.gz
fslchfiletype ANALYZE stats1


cp /mnt/users/js/bbc/holdaal/base.vtk .
cp /mnt/users/js/bbc/holdaal/aal_motor.vtk .
cp /mnt/users/js/bbc/holdaal/channel.vtk .
${PYLABS}/pylabs/diffusion/writefiber_withpaint_may23_2017_qt1
'''