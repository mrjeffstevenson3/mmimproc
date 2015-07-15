import socket


def getlocaldataroot():
    hostname = socket.gethostname()
    if hostname == 'gram':
        return '/home/jasper/mirror/'
    elif hostname == 'JVDB':
        return '/diskArray/mirror/'
    else:
        raise ValueError('Don''t know where data root is on this computer.')
