import os, socket, inspect, pylabs
import petname
from os.path import expanduser, join
from pathlib import *

pylabs_dir = Path(*Path(inspect.getabsfile(pylabs)).parts[:-2])
pylabs_datadir = pylabs_dir / 'data'
pylabs_atlasdir = pylabs_datadir / 'atlases'
moriMNIatlas = pylabs_atlasdir/'mori1_atlas.nii.gz'
JHUMNIatlas = pylabs_atlasdir/'ilabsJHUtracts0_atlas.nii.gz'

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

def getnetworkdataroot():
    hostname = socket.gethostname()

    if hostname == 'scotty.ilabs.uw.edu':
        return '/media/DiskArray/shared_data/js/'
    elif hostname in ['redshirt.ilabs.uw.edu', 'redshirt', 'uhora.ilabs.uw.edu', 'uhora', 'sulu.ilabs.uw.edu', 'sulu', 'JVDB']:
        return '/mnt/users/js/'
    elif any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', '.dhcp4.washington.edu']):
        return '/Users/mrjeffs/Documents/Research/data'
    else:
        raise ValueError('Don''t know where network data root is on this computer.')


def tempfile(extension='.tmp'):
    return os.path.join('/var/tmp',petname.Generate(3,'-')+extension)

def getpylabspath():
    return os.path.split(os.path.split(inspect.getabsfile(pylabs))[0])[0]

def getgannettpath():
    hostlist = ['redshirt.ilabs.uw.edu', 'scotty.ilabs.uw.edu', 'sulu.ilabs.uw.edu']
    hostname = socket.gethostname()
    if hostname in hostlist:
        gannettpath = join(expanduser('~'), 'Software', 'Gannet2.0')
    if 'Jeffs' in hostname:
        gannettpath = join(expanduser('~'), 'Software', 'Gannet2.0-master')
    return gannettpath
