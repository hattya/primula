#
# primula.core
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations
import dataclasses
import hashlib
import os
import re
from typing import Dict, Iterator, List, Optional, Tuple

from ._typing import Path
from .exception import ProfileError


__all__ = ['Profile', 'Script', 'Function', 'Line']

_SCRIPT = 'SCRIPT  '
_SOURCED = 'Sourced '

_FUNCTION = 'FUNCTION  '
_DEFINED = '    Defined: '
_CALLED = 'Called '

_TOTAL_TIME = 'Total time: '
_SELF_TIME = ' Self time: '

_TOTALS = 'count  total (s)   self (s)'
_TOTALS_NS = 'count     total (s)      self (s)'
_SORT_LIST = 'FUNCTIONS SORTED ON '

_function_re = re.compile(r'\bfu(?:n(?:c(?:t(?:i(?:o(?:n)?)?)?)?)?)?!?\b')


class Profile:

    scripts: Dict[str, Script]
    functions: List[Function]

    def __init__(self, path: Path) -> None:
        self.path = path
        self.scripts = {}
        self.functions = []

        self._lineno = 0
        self._parse()
        self._map_all()

    def _parse(self) -> None:
        with open(self.path, encoding='utf-8') as fp:
            self._fp = fp
            try:
                while True:
                    l = self._readline()
                    if l.startswith(_SCRIPT):
                        self._parse_script(l[len(_SCRIPT):])
                    elif l.startswith(_FUNCTION):
                        self._parse_function(l[len(_FUNCTION):])
                    elif l.startswith(_SORT_LIST):
                        break
                    else:
                        raise self._error('unexpected line')
            finally:
                del self._fp

    def _parse_script(self, name: str) -> None:
        sourced = 0
        total_time = self_time = 0.0
        while True:
            l = self._readline()
            if l.startswith(_SOURCED):
                sourced = int(l.split()[1])
            elif l.startswith(_TOTAL_TIME):
                total_time = float(l.split(':')[1])
            elif l.startswith(_SELF_TIME):
                self_time = float(l.split(':')[1])
            elif l in (_TOTALS, _TOTALS_NS):
                col = len(l)
                break
            elif l:
                raise self._error('cannot parse SCRIPT')

        s = Script(name, sourced, total_time, self_time)
        s.lines.extend(self._parse_lines(col))
        self.scripts[s.path] = s

    def _parse_function(self, name: str) -> None:
        called = 0
        total_time = self_time = 0.0
        defined = None
        while True:
            l = self._readline()
            if l.startswith(_CALLED):
                called = int(l.split()[1])
            elif l.startswith(_TOTAL_TIME):
                total_time = float(l.split(':')[1])
            elif l.startswith(_SELF_TIME):
                self_time = float(l.split(':')[1])
            elif l.startswith(_DEFINED):
                i = l.rfind(':')
                if (i > 0
                    and l[i+1:].isdigit()):
                    # Vim 8.1.2055+
                    off = 1
                else:
                    # Vim 8.1.2054-
                    i = l.rindex(' line ')
                    off = 6
                defined = (l[len(_DEFINED):i], l[i+off:])
            elif l in (_TOTALS, _TOTALS_NS):
                col = len(l)
                break
            elif l:
                raise self._error('cannot parse FUNCTION')

        f = Function(name, called, total_time, self_time)
        if defined:
            f.defined = (os.path.expanduser(defined[0].lstrip()), max(int(defined[1]), 1))
        f.lines.extend(self._parse_lines(col))
        self.functions.append(f)

    def _parse_lines(self, col: int) -> Iterator[Line]:
        while True:
            l = self._readline()
            if not l:
                break
            elif not l[col+1:].lstrip().startswith('\\'):
                # count
                i = len('count')
                s = l[:i].lstrip()
                count = int(s) if s else None
                # total time
                j = i + (col - i) // 2
                s = l[i+1:j].lstrip()
                total_time = float(s) if s else None
                # self time
                s = l[j+1:col].lstrip()
                self_time = float(s) if s else None
            yield Line(count, total_time, self_time, l[col+1:])

    def _readline(self) -> str:
        l = self._fp.readline().rstrip(os.linesep)
        self._lineno += 1
        return l

    def _error(self, msg: str) -> Exception:
        return ProfileError(msg, str(self.path), self._lineno)

    def _map_all(self) -> None:
        # by defined
        unknown: Dict[bytes, List[Function]] = {}
        for f in self.functions:
            if f.defined:
                self._map(self.scripts[f.defined[0]], f.defined[1], f)
            else:
                m = hashlib.new('sha512')
                for l in f.lines:
                    m.update(l.line.encode('utf-8'))
                k = m.digest()
                if k not in unknown:
                    unknown[k] = []
                unknown[k].append(f)
        if not unknown:
            return

        # by brute force
        functions = [v[0] for v in unknown.values() if len(v) == 1]
        for s in self.scripts.values():
            i = 0
            while True:
                sl = s.lines[i]
                i += 1
                if i >= len(s.lines):
                    break
                elif (sl.count is None
                      or not _function_re.search(sl.line)):
                    continue
                for f in functions:
                    j = self._map(s, i, f)
                    if f.mapped:
                        functions.remove(f)
                        i = j
                        break

    def _map(self, script: Script, defined: int, function: Function) -> int:
        i = defined
        for fl in function.lines:
            sl = script.lines[i]
            j = i + 1
            if sl.line != fl.line:
                # check for line continuation
                line = sl.line
                for sl in script.lines[j:]:
                    next_line = sl.line.lstrip()
                    if not next_line.startswith('\\'):
                        break
                    line += next_line[1:]
                    j += 1
                if line != fl.line:
                    # revert
                    for sl in script.lines[defined:i]:
                        sl.count = sl.total_time = sl.self_time = None
                    return -1
            for sl in script.lines[i:j]:
                sl.count, sl.total_time, sl.self_time = fl.count, fl.total_time, fl.self_time
            i = j
        else:
            function.mapped = True
        return i


@dataclasses.dataclass
class Script:

    path: str
    sourced: int
    total_time: float
    self_time: float
    lines: List[Line] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Function:

    name: str
    defined: Optional[Tuple[str, int]] = dataclasses.field(default=None, init=False)
    called: int
    total_time: Optional[float]
    self_time: Optional[float]
    lines: List[Line] = dataclasses.field(default_factory=list)

    mapped: bool = dataclasses.field(default=False, init=False)


@dataclasses.dataclass
class Line:

    count: Optional[int]
    total_time: Optional[float]
    self_time: Optional[float]
    line: str
