# first set global root data directory
import pylabs
pylabs.datadir.target = 'jaba'
from pathlib import *
import numpy as np

from pylabs.utils import *

def inject_vol_data_into_vtk(working_dir, vol_fname, vtk_infname, vtk_outfname):
    results = (,)

    with WorkingContext(working_dir):


        with open('usechannel.txt', 'w') as uc:
            uc.write('1\n')

        with open('procmethod.txt', 'w') as pm:
             pm.write('1\n')


        results += run_subprocess(vol2fiber)


    return

'''
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