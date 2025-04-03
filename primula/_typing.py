#
# primula._typing
#
#   Copyright (c) 2024-2025 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

import os
import types
from typing import Union


__all__ = ['MorF', 'Path']

MorF = Union[types.ModuleType, str]
Path = Union[str, os.PathLike[str]]
