#
# primula.cli
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations
from collections.abc import Iterable
import optparse
import os
import subprocess
import sys
from typing import cast, Any, Optional

import coverage
import coverage.cmdline
import coverage.config
import coverage.control

from . import __version__, core, plugin
from .exception import ProfileError


__all__ = ['run']

_FILE_TRACER = f'{__package__}.{plugin.VimScriptPlugin.__name__}'
# defaults values
_ENVIRON = 'PROFILE'
_PROFILE = 'profile.txt'


def run(args: Optional[list[str]] = None) -> None:
    sys.exit(coverage.cmdline.main(args))


class _CoverageScript(coverage.cmdline.CoverageScript):

    def do_run(self, options: optparse.Values, args: list[str]) -> int:
        if not args:
            coverage.cmdline.show_help("Nothing to do.")
            return coverage.cmdline.ERR

        if options.append:
            self.coverage.load()
        # prevent to install tracer
        self.coverage._init()
        self.coverage._init_for_start()
        self.coverage._post_init()
        assert self.coverage._inorout is not None
        self.coverage._inorout.warn_conflicting_settings()
        self.coverage._inorout.warn_already_imported_files()
        # options
        plugin_options = cast('dict[str, str]', self.coverage.config.get_plugin_options(__package__))
        name = plugin_options.get('environ') or _ENVIRON
        os.environ[name] = plugin_options.get('profile') or _PROFILE
        try:
            args[0] = self._which(args[0])
            proc = subprocess.run(args)
            self.coverage.combine([os.environ[name]])
        finally:
            self.coverage.save()
        return coverage.cmdline.ERR if proc.returncode else coverage.cmdline.OK

    def _which(self, name: str) -> str:
        parent, name = os.path.split(name)
        cands: list[str] = []
        if sys.platform == 'win32':
            parent = parent.replace('/', os.sep)
            cands += (name + ext for ext in os.environ['PATHEXT'].split(os.pathsep))
        cands.append(name)
        for p in (parent,) if parent else os.environ['PATH'].split(os.pathsep):
            for n in cands:
                path = os.path.join(p, n)
                if os.path.isfile(path):
                    return path
        raise coverage.CoverageException(f'Could not find command: {name}')


class _Coverage(coverage.control.Coverage):

    def combine(self, data_paths: Optional[Iterable[str]] = None, *args: Any, **kwargs: Any) -> None:
        paths = []
        profs = []
        if data_paths:
            for path in data_paths:
                if os.path.isfile(path):
                    try:
                        p = core.Profile(path)
                    except ProfileError:
                        paths.append(path)
                    else:
                        for f in p.functions:
                            if not (f.mapped
                                    or f.name.startswith(core._LAMBDA)):
                                self._warn(f'Could not find line for function: {f.name}')
                        profs.append(p)
        try:
            super().combine(paths, *args, **kwargs)
        except coverage.CoverageException as e:
            if not ('no data' in str(e).lower()
                    and profs):
                raise

        assert self._data is not None
        file_tracers = {}
        if self.config.branch:
            arcs: dict[str, list[tuple[int, int]]] = {}
            for p in profs:
                for s in p.scripts.values():
                    file_tracers[s.path] = _FILE_TRACER
                    arcs[s.path] = []
                    i = -1
                    for j, l in enumerate(s.lines, 1):
                        if not l.line.lstrip().startswith('\\'):
                            if l.count:
                                arcs[s.path].append((i, j))
                            i = j
                    arcs[s.path].append((i, -1))
            self._data.add_arcs(arcs)
        else:
            lines: dict[str, list[int]] = {}
            for p in profs:
                for s in p.scripts.values():
                    file_tracers[s.path] = _FILE_TRACER
                    lines[s.path] = []
                    for i, l in enumerate(s.lines, 1):
                        if (not l.line.lstrip().startswith('\\')
                            and l.count):
                            lines[s.path].append(i)
            self._data.add_lines(lines)
        self._data.add_file_tracers(file_tracers)


class _CoverageConfig(coverage.config.CoverageConfig):

    def __init__(self) -> None:
        super().__init__()
        self.__plugins = [__package__]

    @property
    def plugins(self) -> list[str]:
        return self.__plugins

    @plugins.setter
    def plugins(self, plugins: list[str]) -> None:
        # automatically load primula
        if __package__ not in plugins:
            plugins.append(__package__)
        self.__plugins = plugins


# help
coverage.cmdline.HELP_TOPICS['help'] = (coverage.cmdline.HELP_TOPICS['help']
                                        .replace('Coverage.py,', f'{__package__.title()} on coverage.py', 1)
                                        .replace('Python program', 'Vim script', 1))
# minimum_help
coverage.cmdline.HELP_TOPICS['minimum_help'] = (f'Code coverage for Vim script, version {__version__}. '
                                                + coverage.cmdline.HELP_TOPICS['minimum_help'].split('. ', 1)[1])
# version
coverage.cmdline.HELP_TOPICS['version'] = f'{__package__}, version {__version__}'
# run
_parser = (coverage.cmdline.COMMANDS if coverage.version_info >= (6, 3) else coverage.cmdline.CMDS)['run']
_parser.remove_option(coverage.cmdline.Opts.concurrency.get_opt_string())
_parser.remove_option(coverage.cmdline.Opts.module.get_opt_string())
_parser.remove_option(coverage.cmdline.Opts.pylib.get_opt_string())
_parser.remove_option(coverage.cmdline.Opts.parallel_mode.get_opt_string())
_parser.remove_option(coverage.cmdline.Opts.timid.get_opt_string())
_parser.set_usage(_parser.usage
                  .replace('pyfile', 'command')
                  .replace('program', 'command'))
_parser.set_description(_parser.description
                        .replace('Python program', 'command'))
del _parser

coverage.cmdline.CoverageScript = _CoverageScript
coverage.cmdline.Coverage = _Coverage
coverage.cmdline.CoverageConfig = coverage.config.CoverageConfig = _CoverageConfig
