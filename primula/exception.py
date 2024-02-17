#
# primula.exception
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

__all__ = ['PrimulaError', 'ProfileError']


class PrimulaError(Exception):
    pass


class ProfileError(PrimulaError):

    def __init__(self, msg: str, path: str, lineno: int) -> None:
        super().__init__(msg)
        self.path = path
        self.lineno = lineno
