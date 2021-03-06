import mmimproc as ip
import os
os.environ["FSLMULTIFILEQUIT"] = 'FALSE'
import socket, inspect, platform
import petname
from mmimproc.utils import which
from os.path import expanduser, join
from pathlib import *

hostname = socket.gethostname()
# hostnames with functioning gpus
working_gpus = ['redshirt.ilabs.uw.edu', 'redshirt', 'scotty', 'scotty.ilabs.uw.edu', 'mccoy', 'mccoy.ilabs.uw.edu',
                'uhora', 'uhora.ilabs.uw.edu', 'spock', 'spock.ilabs.uw.edu', ]

mmimproc_dir = Path(*Path(inspect.getabsfile(ip)).parts[:-2])
mmimproc_datadir = mmimproc_dir / 'data'
mmimproc_atlasdir = mmimproc_datadir / 'atlases'
mmimproc_atlaslabelsdir = mmimproc_datadir / 'atlaslabels'
moriMNIatlas = mmimproc_atlasdir/'mori1_atlas.nii.gz'
JHUMNIatlas = mmimproc_atlasdir/'ilabsJHUtracts0_atlas.nii.gz'
JHUtracts_prob_atlas = mmimproc_atlasdir / 'JHU-ICBM-tracts-prob-1mm.nii.gz'
MNI1mm_T1 = mmimproc_atlasdir/'MNI152_T1_1mm.nii.gz'
MNI1mm_T1_mask = mmimproc_atlasdir/'MNI152_T1_1mm_mask.nii'
MNI1mm_T1_brain = mmimproc_atlasdir/'MNI152_T1_1mm_brain.nii.gz'
MNI1mm_T1_brain_mask = mmimproc_atlasdir/'MNI152_T1_1mm_brain_mask.nii.gz'
# MNI1mm_T2 = mmimproc_atlasdir/'MNI152_T2_1mm.nii.gz'
MNI1mm_T2_brain = mmimproc_atlasdir/'MNI152_T2_1mm_brain.nii'
MNI1mm_T2_brain_dwi = mmimproc_atlasdir/'MNI152_T2_1mm_brain_dwi.nii'
MNI1mm_T1_qa_mask = mmimproc_atlasdir/'MNI152_T1_1mm_qa_mask.nii.gz'
meg_head_mask = mmimproc_atlasdir/'MNI152_T1_1mm_meg_mask.nii'
# false input model for todd's vol2fiber fortran
aal_motor = mmimproc_atlasdir/'aal_motor.vtk'
aal_base = mmimproc_atlasdir/'base.vtk'
aal_channel = mmimproc_atlasdir/'channel.vtk'

# todds fortran programs
vol2fiber = mmimproc_dir/'mmimproc/diffusion/writefiber_withpaint_aug03_2018_qt1_noconversion'
vol2myelin_density = mmimproc_dir/'mmimproc/diffusion/writefiber_withpaint_aug13_2018_myelin_density'


mnicom = mmimproc_atlasdir /'MNI152_T1_1mm_8kcomroi.nii'
mnimask = mmimproc_atlasdir /'MNI152_T1_1mm_mask.nii'
mniT2com = mmimproc_atlasdir /'MNI152_T2_1mm_8kcomroi.nii'
mniT2comdwi = mmimproc_atlasdir /'MNI152_T2_1mm_8kcomroi_dwi.nii'
mniT2combr = mmimproc_atlasdir /'MNI152_T2_1mm_brain_8kcomroi.nii'

def getlocaldataroot():
    hostname = socket.gethostname()

    if hostname == 'gram':
        return '/home/jasper/mirror/js/'
    elif hostname == 'JVDB':
        return '/diskArray/mirror/js/'
    elif hostname == 'scotty.ilabs.uw.edu':
        return '/media/DiskArray/shared_data/js/'
    elif hostname in ['redshirt.ilabs.uw.edu', 'redshirt']:
        return '/redshirt_array/data/'
    else:
        raise ValueError('Don''t know where data root is on this computer.')

def getnetworkdataroot(verbose=True):
    hostname = socket.gethostname()
    if ip.datadir.target == 'kl4' and any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3',
                                       'Jeffs-MacBook-Pro.local' , '.dhcp4.washington.edu']):
        print('found mrjeffs laptop. using jump drive datadir. datadir=/Volumes/KUHL_LAB4')
        return Path('/Volumes/KUHL_LAB4')

def tempfile(extension='.tmp'):
    return join('/var/tmp',petname.Generate(3,'-')+extension)

def getippath():
    return os.path.split(os.path.split(inspect.getabsfile(ip))[0])[0]

def getgannettpath():
    hostlist = ['redshirt.ilabs.uw.edu', 'scotty.ilabs.uw.edu', 'sulu.ilabs.uw.edu', 'redshirt', 'uhora']
    hostname = socket.gethostname()
    if hostname in hostlist:
        gannettpath = join(expanduser('~'), 'Software', 'Gannet2.0')
    if any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', '.dhcp4.washington.edu']):
        print('found dhcp hostname. assuming mrjeffs laptop' )
        gannettpath = join(expanduser('~'), 'Software', 'Gannet2.0')
    return gannettpath

def getbctpath():
    hostlist = ['redshirt.ilabs.uw.edu', 'scotty.ilabs.uw.edu', 'sulu.ilabs.uw.edu']
    hostname = socket.gethostname()
    if hostname in hostlist:
        bctpath = join(expanduser('~'), 'Software', 'BCT', '2017_01_15_BCT')
    if any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', '.dhcp4.washington.edu']):
        print('found dhcp hostname. assuming mrjeffs laptop' )
        bctpath = join(expanduser('~'), 'Software', 'BCT', '2017_01_15_BCT')
    return bctpath

def getafqpath():
    hostlist = ['redshirt.ilabs.uw.edu', 'uhora.ilabs.uw.edu', 'scotty.ilabs.uw.edu', 'sulu.ilabs.uw.edu', 'redshirt', 'uhora', 'scotty', 'sulu']
    hostname = socket.gethostname()
    if hostname in hostlist:
        afqpath = join(expanduser('~'), 'Software', 'AFQ')
    return afqpath

def getvistasoftpath():
    hostlist = ['redshirt.ilabs.uw.edu', 'uhora.ilabs.uw.edu', 'scotty.ilabs.uw.edu', 'sulu.ilabs.uw.edu', 'redshirt', 'uhora', 'scotty', 'sulu']
    hostname = socket.gethostname()
    if hostname in hostlist:
        vistasoftpath = join(expanduser('~'), 'Software', 'vistasoft')
    return vistasoftpath

def test4working_gpu():
    hostname = socket.gethostname()
    if hostname in working_gpus:
        return True
    else:
        print('current hostname not in working gpu list in mmimproc.utils.paths. using un-accelerated methods.')
        return False

def get_antsregsyn_cmd(quick=False, warps=False, warpts=False, N4bias=False, default_cmd_str=False):
    if N4bias:
        if not Path(os.environ.get('ANTSPATH'), 'N4BiasFieldCorrection').is_file():
            raise ValueError('must have ants installed with N4BiasFieldCorrection in $ANTSPATH directory.')
        else:
            if default_cmd_str:
                return os.environ.get('ANTSPATH') + 'N4BiasFieldCorrection -d 3 -i {infile} -o {outfile}'
            else:
                return Path(os.environ.get('ANTSPATH'), 'N4BiasFieldCorrection')
    if warps:
        if not Path(os.environ.get('ANTSPATH'), 'WarpImageMultiTransform').is_file():
            raise ValueError('must have ants installed with WarpImageMultiTransform in $ANTSPATH directory.')
        else:
            return Path(os.environ.get('ANTSPATH'), 'WarpImageMultiTransform')
    if warpts:
        if not Path(os.environ.get('ANTSPATH'), 'WarpTimeSeriesImageMultiTransform').is_file():
            raise ValueError('must have ants installed with WarpTimeSeriesImageMultiTransform in $ANTSPATH directory.')
        else:
            return Path(os.environ.get('ANTSPATH'), 'WarpTimeSeriesImageMultiTransform')
    if quick:
        if not (Path(os.environ.get('ANTSPATH')) / 'antsRegistrationSyNQuick.sh').is_file():
            raise ValueError('must have ants installed with antsRegistrationSyNQuick.sh in $ANTSPATH directory.')
        else:
            if default_cmd_str:
                return os.environ.get('ANTSPATH') + 'antsRegistrationSyNQuick.sh -d 3 -m {moving} -f {fixed} -o {outfile} -n 30 -t s -p f -j 1 -s 10 -r 1'
            else:
                return Path(os.environ.get('ANTSPATH'), 'antsRegistrationSyNQuick.sh')
    if not (Path(os.environ.get('ANTSPATH')) / 'antsRegistrationSyN.sh').is_file():
        raise ValueError('must have ants installed with antsRegistrationSyN.sh in $ANTSPATH directory.')
    else:
        if default_cmd_str:
            antsRegistrationSyN = os.environ.get('ANTSPATH') + 'antsRegistrationSyN.sh -d 3 -m {moving} -f {fixed} -o {outfile} -n 30 -t s -p f -j 1 -s 10 -r 1'
            return antsRegistrationSyN
        else:
            antsRegistrationSyN = Path(os.environ.get('ANTSPATH'), 'antsRegistrationSyN.sh')
            return antsRegistrationSyN

def getslicercmd(ver='stable', stable_linux_ver='Slicer-4.8.1-linux-amd64', dev_linux_ver='Slicer-4.9.0-2018-02-08-linux-amd64', dev_mac_ver='Slicer_stable_rel_4p10p1_jan-18-2019.app', stable_mac_ver='Slicer_stable_rel_4p10p1_jan-18-2019.app'):
    if platform.system() == 'Darwin' and ver == 'dev':
        slicer_path = Path('/Applications', dev_mac_ver, 'Contents/MacOS/Slicer --launch ')
    elif platform.system() == 'Darwin' and ver == 'stable':
        slicer_path = Path('/Applications', stable_mac_ver, 'Contents/MacOS/Slicer --launch ')
    elif platform.system() == 'Linux' and ver == 'dev':
        slicer_path = Path(*Path(inspect.getabsfile(ip)).parts[:-3]) / dev_linux_ver / 'Slicer --launch '
    elif platform.system() == 'Linux' and ver == 'stable':
        slicer_path = Path(*Path(inspect.getabsfile(ip)).parts[:-3]) / stable_linux_ver / 'Slicer --launch '
    if not slicer_path.parent.is_dir():
        raise ValueError('Slicer path not found for {slicer_path}'.format(**{'slicer_path': slicer_path}))
    return slicer_path

def getspmpath():
    hostname = socket.gethostname()
    if platform.system() == 'Darwin' and any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', '.dhcp4.washington.edu']):
        spm_path = Path(mmimproc_dir.parent, 'spm12b')

    elif platform.system() == 'Linux' and hostname in ['scotty', 'scotty.ilabs.uw.edu', 'redshirt.ilabs.uw.edu', 'redshirt', 'uhora', 'uhora.ilabs.uw.edu']:
        spm_path = Path(mmimproc_dir.parent, 'spm12')

    tpm_path = spm_path / 'tpm' / 'TPM.nii'
    return spm_path, tpm_path

def getqccmd():
    if platform.system() == 'Linux':
        dwi_qc = mmimproc_dir / 'mmimproc' / 'diffusion' / 'dti_qc_correlation_single_feb2018_gnuplot'
        plot_vols = mmimproc_dir / 'mmimproc' / 'diffusion' / 'makegnuplot_dtiqc.txt'
    if platform.system() == 'Darwin':
        raise ValueError('not implemented for Mac os yet.')
        #dwi_qc = mmimproc_dir / 'diffusion' / 'mac_dti_qc_correlation_single_feb2018'
        #if not dwi_qc.is_file():
        #    run_subprocess(['gfortran '+str(dwi_qc.parents/'dti_qc_correlation_single_feb2018.f')+' -o '+str(dwi_qc)+' -ffixed-line-length-none'])

    if not 'gnuplot' in which('gnuplot'):
        raise ValueError('Dependency error. Cannot find working copy of gnuplot in PATH.')
#    if not 'dti_qc_correlation_single_feb2018' in which('dti_qc_correlation_single_feb2018'):
#        raise ValueError('Error finding todds fortran qc program in mmimproc/diffusion.')
    return dwi_qc, plot_vols

def getoctavecmd():
    if not 'gnuplot' in which('gnuplot'):
        raise ValueError('Dependency error. Cannot find working copy of gnuplot in PATH.')
    if platform.system() == 'Linux':
        raise ValueError('not implemented for Mac os yet.')
    if platform.system() == 'Darwin' and any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3',
                                       'Jeffs-MacBook-Pro.local']):
        octave = '/Applications/Octave-5.2.0.app/Contents/Resources/usr/bin/octave-octave-app@5.2.0 --no-gui'
        return octave
