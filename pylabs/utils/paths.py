import os, socket
import petname


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
    elif hostname == 'Jeffs-MBP-3' or hostname == 'Jeffs-MacBook-Pro-3.local' or hostname == 'D-140-142-55-182.dhcp4.washington.edu':
        return '/Users/mrjeffs/Documents/Research/data'
    else:
        raise ValueError('Don''t know where data root is on this computer.')


def tempfile(extension='.tmp'):
    return os.path.join('/var/tmp',petname.Generate(3,'-')+extension)
