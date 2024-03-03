#
# primula
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

__author__ = 'Akinori Hattori <hattya@gmail.com>'
try:
    from .__version__ import version as __version__
except ImportError:
    __version__ = 'unknown'

from .core import *
from .exception import *
try:
    from .plugin import *
except ImportError:
    pass
