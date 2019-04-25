# -*- coding: utf-8 -*-

__version__ = '0.1.git'

import mmimproc
from mmimproc.utils import *

datadir = RootDataDir()

popts = PylabsOptions()

mmimproc.datadir.target = 'js5'   # main brain studio nfs network drive

mmimproc.h5wait_interval = 30  # seconds to wait before retry

mmimproc.max_intervals = 10  # or about 5 min else something is wrong

