#
# primula._typing
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

import os
from typing import Union


__all__ = ['Path']

Path = Union[str, os.PathLike[str]]
