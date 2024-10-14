#
# primula.plugin
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations
from collections.abc import Iterable
import os
import re
from typing import Any, Optional, Union

import coverage
import coverage.plugin_support


__all__ = ['coverage_init']


def coverage_init(reg: coverage.plugin_support.Plugins, options: dict[str, Any]) -> None:
    reg.add_file_tracer(VimScriptPlugin(
        cond=_to_bool(options.get('cond'), True),
        end=_to_bool(options.get('end'), False),
    ))


def _to_bool(s: Optional[str] = None, default: bool = False) -> bool:
    return s.lower() not in ('', '0', 'false', 'no', 'off') if s is not None else default


class VimScriptPlugin(coverage.CoveragePlugin):

    def __init__(self, cond: bool, end: bool) -> None:
        pat = ['$', '"']
        cmds = []
        if not cond:
            cmds += [
                'elsei(?:f)?',                                     # :elsei[f]
                'cat(?:c(?:h)?)?',                                 # :cat[ch]
                'fina(?:l(?:l(?:y)?)?)?',                          # :fina[lly]
            ]
        if not end:
            cmds += [
                'en(?:d(?:i(?:f)?)?)?',                            # :en[dif]
                'endw(?:h(?:i(?:l(?:e)?)?)?)?',                    # :endw[hile]
                'endfo(?:r)?',                                     # :endfo[r]
                'endt(?:r(?:y)?)?',                                # :endt[ry]
                'endf(?:u(?:n(?:c(?:t(?:i(?:o(?:n)?)?)?)?)?)?)?',  # :endf[unction]
            ]
        if cmds:
            pat.append(fr'\b(?:{"|".join(cmds)})\b')
        self._noexec_line_re = re.compile(fr'^\s*(?:{"|".join(pat)})')

    def file_reporter(self, path: str) -> Union[coverage.FileReporter, str]:
        return _FileReporter(path, self._noexec_line_re)

    def find_executable_files(self, path: str) -> Iterable[str]:
        for root, _, files in os.walk(path):
            for f in files:
                if f.endswith('.vim'):
                    yield os.path.join(root, f)


class _FileReporter(coverage.FileReporter):

    def __init__(self, path: str, noexec_line_re: re.Pattern[str]) -> None:
        super().__init__(path)
        self._noexec_line_re = noexec_line_re

    def lines(self) -> set[int]:
        lines = set()
        for i, l in enumerate(self.source().splitlines(), 1):
            if not (l.lstrip().startswith('\\')
                    or self._noexec_line_re.match(l)):
                lines.add(i)
        return lines
