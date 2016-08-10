import os, socket, inspect, pylabs
import petname
from os.path import expanduser, join


def getlocaldataroot():
    hostname = socket.gethostname()

    if hostname == 'gram':
        return '/home/jasper/mirror/js/'
    elif hostname == 'JVDB':
        return '/diskArray/mirror/js/'
    elif hostname == 'scotty.ilabs.uw.edu':
        return '/media/DiskArray/shared_data/js/'
    elif hostname == 'redshirt.ilabs.uw.edu':
        return '/redshirt_array/data/'
    elif hostname == 'Jeffs-MBP-3' or hostname == 'Jeffs-MacBook-Pro-3.local' or hostname == 'D-69-91-166-176.dhcp4.washington.edu':
        return '/Users/mrjeffs/Documents/Research/data'
    else:
        raise ValueError('Don''t know where data root is on this computer.')

def getnetworkdataroot():
    hostname = socket.gethostname()

    if hostname == 'JVDB':
        return '/mnt/users/js/'
    elif hostname == 'scotty.ilabs.uw.edu':
        return '/media/DiskArray/shared_data/js/'
    elif hostname == 'sulu.ilabs.uw.edu':
        return '/mnt/users/js/'
    elif hostname == 'redshirt.ilabs.uw.edu':
        return '/mnt/users/js/'
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
    return gannettpath
