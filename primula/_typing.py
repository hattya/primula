#
# primula._typing
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

import os
import sys
from typing import TYPE_CHECKING, Union


__all__ = ['Path']

if (TYPE_CHECKING
    or sys.version_info >= (3, 9)):
    Path = Union[str, os.PathLike[str]]
else:
    Path = Union[str, os.PathLike]
