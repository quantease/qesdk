# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 23:42:18 2022

@author: ScottStation
"""

import sys
import os
sys.modules["ROOT_DIR"] = os.path.abspath(os.path.dirname(__file__))

from .api import *
from .aio_api import *
from .client import testClient, auth
from .client import __version__




__all__ = [
    "auth",
    "testClient",
    "__version__"
]
__all__.extend(api.__all__)
__all__.extend(aio_api.__all__)