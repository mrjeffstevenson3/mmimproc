# first set global root data directory
import mmimproc
mmimproc.datadir.target = 'jaba'
from pathlib import *
import shutil
import nibabel as nib
from mmimproc.utils import *
mopts = MmimprocOptions()


def inject_vol_data_into_vtk(working_dir, vol_fname, vtk_infname, vtk_outfname, offset_adj=(0, 0, 0)):
    results = ('',)
    with WorkingContext(working_dir):
        vol_fname = Path(vol_fname)
        vtk_infname = Path(vtk_infname)
        if not vol_fname.is_file():
            raise ValueError('Missing input stats injection volume. please check.')
        if not vtk_infname.is_file():
            raise ValueError('Missing vtk file to be injected. please check.')
        vtk_outfname = Path(vtk_outfname)
        shutil.copy(str(vtk_infname), 'f.vtk')
        img = nib.load(str(vol_fname))
        nib.save(img, 'stats1.hdr')
        vol_hdr = run_subprocess(['fslhd -x '+str(vol_fname)])
        for line in vol_hdr[0].splitlines():
            if 'qto_ijk_matrix' in line:
                ijk_off = line.replace('qto_ijk_matrix =', '').split(' ')
                offsets = {'x': float(ijk_off[6]) + offset_adj[0], 'y': float(ijk_off[10]) + offset_adj[1], 'z': float(ijk_off[14]) + offset_adj[2]}
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
        results += run_subprocess([str(vol2fiber)])
        Path('fnew.vtk').rename(vtk_outfname)
    return results      #  "({})".format(", ".join(results))    # fails under some conditions

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
${PYLABS}/mmimproc/diffusion/writefiber_withpaint_may23_2017_qt1
'''