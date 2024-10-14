#
# primula.core
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations
import collections
from collections.abc import Iterator
import dataclasses
import hashlib
import os
import re
from typing import Optional, Union

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

_LAMBDA = '<lambda>'

_function_re = re.compile(r'\bfu(?:n(?:c(?:t(?:i(?:o(?:n)?)?)?)?)?)?!?\b')
_noexec_line_re = re.compile(r'^\s*(?:$|")')


class Profile:

    scripts: dict[str, Script]
    functions: list[Function]

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
        s.lines.extend(self._parse_lines(True, col))
        if s.lines:
            # Vim 8.0.1206-
            self._adjust_script(s)
        self.scripts[s.path] = s

    def _adjust_script(self, script: Script) -> None:
        # first line
        if (script.lines[0].count is None
            and not _noexec_line_re.match(script.lines[0].line)):
            script.lines[0].count = script.sourced
        # last lines with line continuation
        try:
            with open(script.path, encoding='utf-8') as fp:
                lines = fp.read().splitlines()
        except OSError:
            return
        if (len(lines) > len(script.lines)
            and lines[-1].lstrip().startswith('\\')):
            for i, sl in enumerate(script.lines):
                if sl.line != lines[i]:
                    return
            script.lines += (dataclasses.replace(script.lines[-1], line=l) for l in lines[i+1:] if l.lstrip().startswith('\\'))
            if len(script.lines) != len(lines):
                # revert
                script.lines = script.lines[:i+1]

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
        f.lines.extend(self._parse_lines(False, col))
        self.functions.append(f)

    def _parse_lines(self, script: bool, col: int) -> Iterator[Line]:
        ns = col == len(_TOTALS_NS)
        i = len('count')
        while True:
            l = self._readline()
            if not l:
                break
            elif (script
                  and ns):
                if not l[i-1].isdigit():
                    col = len(_TOTALS)
                elif not l[i+3].isdigit():
                    col = l.index(' ', l.index('.'))
                else:
                    col = len(_TOTALS_NS)

            if not l[col+1:].lstrip().startswith('\\'):
                # count
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
        unknown: dict[bytes, list[Function]] = {}
        for f in self.functions:
            if f.name.startswith(_LAMBDA):
                continue
            elif f.defined:
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
            # propagate to nested functions
            for f in self.functions:
                assert f.defined is not None
                s = self.scripts[f.defined[0]]
                i = 0
                for sl in s.lines[f.defined[1]:]:
                    if i >= len(f.lines):
                        break
                    elif sl.line.lstrip().startswith('\\'):
                        continue
                    fl = f.lines[i]
                    if fl.count is None:
                        fl.count, fl.total_time, fl.self_time = sl.count, sl.total_time, sl.self_time
                    i += 1
            return

        # by brute force
        functions = [v[0] for v in unknown.values() if len(v) == 1]
        queue: collections.deque[Union[Script, Function]] = collections.deque(self.functions)
        queue.extend(self.scripts.values())
        rels = {}
        while queue:
            b = queue.popleft()
            i = 0
            while True:
                bl = b.lines[i]
                i += 1
                if i >= len(b.lines):
                    break
                elif (bl.count is None
                      or not _function_re.search(bl.line)):
                    continue
                for f in functions:
                    j = self._map(b, i, f)
                    if f.mapped:
                        functions.remove(f)
                        i = j
                        # relations
                        rels[f.name] = (b, f)
                        if (isinstance(b, Function)
                            and b.name in rels):
                            # propagate to outer functions
                            b, f = rels.pop(b.name)
                            f.mapped = False
                            queue.appendleft(b)
                            functions.append(f)
                        break

    def _map(self, block: Union[Script, Function], defined: int, function: Function) -> int:
        i = defined
        for fl in function.lines:
            bl = block.lines[i]
            j = i + 1
            if bl.line != fl.line:
                # check for line continuation
                line = bl.line
                for bl in block.lines[j:]:
                    next_line = bl.line.lstrip()
                    if not next_line.startswith('\\'):
                        break
                    line += next_line[1:]
                    j += 1
                if line != fl.line:
                    # revert
                    for bl in block.lines[defined:i]:
                        bl.count = bl.total_time = bl.self_time = None
                    return -1
            for bl in block.lines[i:j]:
                if bl.count is None:
                    bl.count, bl.total_time, bl.self_time = fl.count, fl.total_time, fl.self_time
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
    lines: list[Line] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Function:

    name: str
    defined: Optional[tuple[str, int]] = dataclasses.field(default=None, init=False)
    called: int
    total_time: Optional[float]
    self_time: Optional[float]
    lines: list[Line] = dataclasses.field(default_factory=list)

    mapped: bool = dataclasses.field(default=False, init=False)


@dataclasses.dataclass
class Line:

    count: Optional[int]
    total_time: Optional[float]
    self_time: Optional[float]
    line: str
