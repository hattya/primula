#
# base
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

import contextlib
import os
import tempfile
import unittest


__all__ = ['PrimulaTestCase']


class PrimulaTestCase(unittest.TestCase):

    def tempdir(self):
        return tempfile.TemporaryDirectory(prefix='primula-')

    @contextlib.contextmanager
    def tempfile(self):
        fd, path = tempfile.mkstemp(prefix='primula-')
        try:
            os.close(fd)
            yield path
        finally:
            os.unlink(path)
