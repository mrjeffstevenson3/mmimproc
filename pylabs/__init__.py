# -*- coding: utf-8 -*-

__version__ = '0.1.git'

from . import utils
from .utils.paths import RootDataDir
from .utils._options import PylabsOptions

datadir = RootDataDir()

opts = PylabsOptions()