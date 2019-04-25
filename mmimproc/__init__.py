# -*- coding: utf-8 -*-

__version__ = '0.3.6'

import mmimproc
from mmimproc.utils import *
import socket, platform

datadir = RootDataDir()

popts = PylabsOptions()

mmimproc.datadir.target = 'js5'   # global variable used in utils.paths for data root directory

mmimproc.h5wait_interval = 30  # seconds to wait before retry

mmimproc.max_intervals = 10  # or about 5 min else something is wrong

hostname = socket.gethostname()

if mmimproc.datadir.target == 'js5' and platform.system() == 'Darwin' and \
        any(x in hostname for x in ['Jeffs-MacBook-Pro-3.local', 'Jeffs-MBP-3', 'Jeffs-MacBook-Pro.local']):
    mmimproc.fs = Path('/Volumes/JSDRIVE05')
    if mmimproc.fs.is_dir():
        print('found mrjeffs laptop mounted drive datadir=/Volumes/JSDRIVE05')
    else:
        print('JSDRIVE05 drive not mounted. please check. fs variable exists but will not work.')


