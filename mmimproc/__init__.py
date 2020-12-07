# -*- coding: utf-8 -*-
__version__ = '0.4.0'

import mmimproc as ip
from mmimproc.utils import *
import socket, platform

class RootDataDir(object):
    target = 'js'
    pass

datadir = RootDataDir()

mopts = MmimprocOptions()   # global options, should be

ip.h5wait_interval = 30  # seconds to wait before retry

ip.max_intervals = 10  # or about 5 min else something is wrong

hostname = socket.gethostname()

if ip.datadir.target == 'js' and platform.system() == 'Darwin' and \
        any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', 'Jeffs-MacBook-Pro.local']):
    ip.fs_exthd = Path('/Volumes/JSDRIVE05')
    ip.fs_local = Path('/Users/mrjeffs/data')
    ip.fs_cloud = Path('/Users/mrjeffs/data/toddandclark/gdrive_data')
    if ip.fs_exthd.is_dir() and mopts.init_verbose:
        print('found mrjeffs laptop mounted drive datadir=/Volumes/JSDRIVE05')
    elif mopts.init_verbose:
        print('mmimproc.fs_exthd variable exists but will not work until drive JSDRIVE05 mounted.')
        if ip.fs_local.is_dir():
            print('Or set file system to local with fs = mmimproc.fs_local')
        else:
            print('No local data directory option found. Please check.')


