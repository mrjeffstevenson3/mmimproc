import socket


def getlocaldataroot():
    hostname = socket.gethostname()

    if hostname == 'gram':
        return '/home/jasper/mirror/js/'
    elif hostname == 'JVDB':
        return '/diskArray/mirror/js/'
    elif hostname == 'scotty':
        return '/media/DiskArray/shared_data/js/'
    elif hostname == 'redshirt.ilabs.uw.edu':
        return '/redshirt_array/data/'
    else:
        raise ValueError('Don''t know where data root is on this computer.')
