# -*- coding: utf-8 -*-

__version__ = '0.1.git'

import pylabs
from utils import *

datadir = RootDataDir()

popts = PylabsOptions()

pylabs.datadir.target = 'jaba'   # main brain studio nfs network drive

pylabs.h5wait_interval = 30  # seconds

pylabs.max_intervals = 10  # or about 5 min else something is wrong