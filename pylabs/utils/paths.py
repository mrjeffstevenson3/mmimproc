import pylabs
import os, socket, inspect, platform
import petname
from os.path import expanduser, join
from pathlib import *

class RootDataDir(object):
    target = 'scotty'
    pass

# hostnames with functioning gpus
working_gpus = ['redshirt.ilabs.uw.edu', 'scotty.ilabs.uw.edu']

pylabs_dir = Path(*Path(inspect.getabsfile(pylabs)).parts[:-2])
pylabs_datadir = pylabs_dir / 'data'
pylabs_atlasdir = pylabs_datadir / 'atlases'
moriMNIatlas = pylabs_atlasdir/'mori1_atlas.nii.gz'
JHUMNIatlas = pylabs_atlasdir/'ilabsJHUtracts0_atlas.nii.gz'
MNI1mm_T1 = pylabs_atlasdir/'MNI152_T1_1mm.nii.gz'
MNI1mm_T1_brain = pylabs_atlasdir/'MNI152_T1_1mm_brain.nii.gz'
MNI1mm_T1_brain_mask = pylabs_atlasdir/'MNI152_T1_1mm_brain_mask.nii.gz'
MNI1mm_T2 = pylabs_atlasdir/'MNI152_T2_1mm.nii.gz'
MNI1mm_T2_brain = pylabs_atlasdir/'MNI152_T2_1mm_brain.nii.gz'

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
    elif hostname == 'Jeffs-MBP-3' or hostname == 'Jeffs-MacBook-Pro-3.local' or hostname == 'D-140-142-110-82.dhcp4.washington.edu':
        return '/Users/mrjeffs/Documents/Research/data'
    else:
        raise ValueError('Don''t know where data root is on this computer.')

def getnetworkdataroot(verbose=True):
    hostname = socket.gethostname()
    if pylabs.datadir.target == 'scotty':
        if verbose:
            print('setting root data directory to scotty.')
        if hostname == 'scotty.ilabs.uw.edu':
            return '/media/DiskArray/shared_data/js/'
        elif hostname in ['redshirt.ilabs.uw.edu', 'redshirt', 'uhora.ilabs.uw.edu', 'uhora', 'sulu.ilabs.uw.edu', 'sulu', 'JVDB', 'spock', 'spock.ilabs.uw.edu']:
            return '/mnt/users/js/'
        elif any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', '.dhcp4.washington.edu']):
            return '/Users/mrjeffs/Documents/Research/data'
        else:
            raise ValueError('Dont know where scotty network root data dir is on this computer.')
    if pylabs.datadir.target == 'jaba':
        if verbose:
            print('setting root data directory to jaba.')
        if hostname in ['scotty.ilabs.uw.edu', 'scotty', 'redshirt.ilabs.uw.edu', 'redshirt', 'uhora.ilabs.uw.edu', 'uhora', 'sulu.ilabs.uw.edu', 'sulu', 'JVDB', 'spock', 'spock.ilabs.uw.edu']:
            return '/brainstudio/data'
        elif any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', '.dhcp4.washington.edu']):
            print('found mrjeffs laptop. using local datadir. datadir= ', pylabs.datadir.target)
            return '/Users/mrjeffs/Documents/Research/data'
        else:
            raise ValueError('Dont know where jaba network root data dir is on this computer.')
    if pylabs.datadir.target == 'kl4' and any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', '.dhcp4.washington.edu']):
        print('found mrjeffs laptop. using jump drive datadir. datadir=/Volumes/KUHL_LAB4')
        return '/Volumes/KUHL_LAB4'


def tempfile(extension='.tmp'):
    return os.path.join('/var/tmp',petname.Generate(3,'-')+extension)

def getpylabspath():
    return os.path.split(os.path.split(inspect.getabsfile(pylabs))[0])[0]

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

def test4working_gpu():
    hostname = socket.gethostname()
    if hostname in working_gpus:
        return True
    else:
        print('current hostname not in working gpu list in pylabs.utils.paths. using un-accelerated methods.')
        return False

def get_antsregsyn_cmd(quick=False, warps=False, warpts=False):
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
            return Path(os.environ.get('ANTSPATH'), 'antsRegistrationSyNQuick.sh')
    if not (Path(os.environ.get('ANTSPATH')) / 'antsRegistrationSyN.sh').is_file():
        raise ValueError('must have ants installed with antsRegistrationSyN.sh in $ANTSPATH directory.')
    else:
        antsRegistrationSyN = Path(os.environ.get('ANTSPATH'), 'antsRegistrationSyN.sh')
        return antsRegistrationSyN

def getslicercmd(linux_ver='Slicer-4.7.0-2017-03-12-linux-amd64', mac_ver='Slicer_dev4p7_2-21-2017.app'):
    if platform.system() == 'Darwin':
        slicer_path = Path('/Applications', mac_ver, 'Contents/MacOS/Slicer --launch ')
    elif platform.system() == 'Linux':
        slicer_path = Path(*Path(inspect.getabsfile(pylabs)).parts[:-3]) / linux_ver / 'Slicer --launch '
    if not slicer_path.parent.is_dir():
        raise ValueError('Slicer path not found for ' + str(slicer_path))
    return slicer_path

def getspmpath():
    hostname = socket.gethostname()
    if platform.system() == 'Darwin' and any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', '.dhcp4.washington.edu']):
        spm_path = Path(pylabs_dir.parent, 'spm12b')

    elif platform.system() == 'Linux' and hostname in ['scotty', 'scotty.ilabs.uw.edu', 'redshirt.ilabs.uw.edu', 'redshirt', 'uhora', 'uhora.ilabs.uw.edu']:
        spm_path = Path(pylabs_dir.parent, 'spm12')

    tpm_path = spm_path / 'tpm' / 'TPM.nii'
    return spm_path, tpm_path
