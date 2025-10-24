#
# primula.cli
#
#   Copyright (c) 2024-2025 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations
from collections.abc import Iterable
import optparse
import os
import subprocess
import sys
from typing import cast, no_type_check, Any

import coverage
import coverage.cmdline
import coverage.config
import coverage.control
import coverage.env
try:
    import coverage.report_core as coverage_report
except ImportError:
    import coverage.report as coverage_report

from . import __version__, core, lcov, plugin
from ._typing import MorF
from .exception import ProfileError


__all__ = ['run']

_FILE_TRACER = f'{__package__}.{plugin.VimScriptPlugin.__name__}'
# defaults values
_ENVIRON = 'PROFILE'
_PROFILE = 'profile.txt'
_LCOV_OUTPUT = 'lcov.info'


def run(args: list[str] | None = None) -> None:
    sys.exit(coverage.cmdline.main(args))


class _CoverageScript(coverage.cmdline.CoverageScript):

    if coverage.version_info < (6, 3):
        @no_type_check
        def command_line(self, argv: list[str]) -> int:
            if (argv
                and argv[0] == 'lcov'):
                argv[0] = 'xml'
                coverage.cmdline.CMDS['xml'] = coverage.cmdline.CMDS['lcov']
                coverage.cmdline.Coverage.xml_report = coverage.cmdline.Coverage.lcov_report
            return super().command_line(argv)

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
        plugin_options = cast(dict[str, str], self.coverage.config.get_plugin_options(__package__))
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
                if os.path.isfile(path := os.path.join(p, n)):
                    return path
        raise coverage.CoverageException(f'Could not find command: {name}')


class _Coverage(coverage.control.Coverage):

    def combine(self, data_paths: Iterable[str] | None = None, *args: Any, **kwargs: Any) -> None:
        paths = []
        profs = []
        if data_paths:
            self._init()
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

    def lcov_report(self, morfs: Iterable[MorF] | None = None,
                    outfile: str | None = None, ignore_errors: bool | None = None,
                    omit: str | list[str] | None = None, include: str | list[str] | None = None,
                    contexts: list[str] | None = None, skip_empty: bool | None = None) -> float:
        outfile = outfile or _LCOV_OUTPUT
        plugin_options = cast(dict[str, str], self.config.get_plugin_options(__package__))
        try:
            p = core.Profile(plugin_options.get('profile') or _PROFILE)
        except (OSError, ProfileError):
            p = None
        with coverage.control.override_config(self,
                                              ignore_errors=ignore_errors,
                                              report_omit=omit,
                                              report_include=include,
                                              report_contexts=contexts):
            return coverage_report.render_report(outfile, lcov.LCOVReporter(self, p), morfs,
                                                 *(self._message,) if coverage.version_info >= (6, 1) else ())


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


if coverage.version_info < (6, 3):
    import copy

    coverage.cmdline.Opts.output_lcov = _option = copy.copy(coverage.cmdline.Opts.output_xml)
    assert _option.help is not None
    _option.help = (_option.help
                    .replace('XML', 'LCOV')
                    .replace('coverage.xml', _LCOV_OUTPUT))
    del _option

_COMMANDS = coverage.cmdline.COMMANDS if coverage.version_info >= (6, 3) else coverage.cmdline.CMDS
_HELP_TOPICS = coverage.cmdline.HELP_TOPICS
# lcov
_COMMANDS['lcov'] = _parser = coverage.cmdline.CmdOptionParser(
    'lcov',
    [
        opt for a in [
            'datafle_input',  # 7.3.3+
            'input_datafile', # 6.3    ... 7.3.2
            'fail_under',
            'ignore_errors',
            'include',
            'omit',
            'output_lcov',
            'quiet',          # 6.1+
        ]
        if (opt := getattr(coverage.cmdline.Opts, a, None))
    ] + coverage.cmdline.GLOBAL_ARGS,
    usage='[options] [modules]',
    description='Generate an LCOV report of coverage results.',
)
if coverage.version_info < (6, 3):
    _parser.set_defaults(action='xml')
    _HELP_TOPICS['help'] = _HELP_TOPICS['help'].replace('  report', f'  lcov        {_parser.description}\n            report')
# run
_parser = _COMMANDS['run']
_parser.remove_option(coverage.cmdline.Opts.concurrency.get_opt_string())
_parser.remove_option(coverage.cmdline.Opts.module.get_opt_string())
_parser.remove_option(coverage.cmdline.Opts.pylib.get_opt_string())
_parser.remove_option(coverage.cmdline.Opts.parallel_mode.get_opt_string())
_parser.remove_option(coverage.cmdline.Opts.timid.get_opt_string())
assert _parser.usage is not None
_parser.set_usage(_parser.usage
                  .replace('pyfile', 'command')
                  .replace('program', 'command'))
assert _parser.description is not None
_parser.set_description(_parser.description
                        .replace('Python program', 'command'))
# help
_HELP_TOPICS['help'] = (_HELP_TOPICS['help']
                        .replace('Coverage.py,', f'{__package__.title()} on coverage.py', 1)
                        .replace('Python program', 'Vim script', 1))
# minimum_help
_HELP_TOPICS['minimum_help'] = (f'Code coverage for Vim script, version {__version__}. '
                                f'{_HELP_TOPICS["minimum_help"].split(". ", 1)[1]}')
# version
_HELP_TOPICS['version'] = f'{__package__}, version {__version__}'

del _parser, _HELP_TOPICS, _COMMANDS

coverage.cmdline.CoverageScript = _CoverageScript
coverage.cmdline.Coverage = _Coverage
coverage.cmdline.CoverageConfig = coverage.config.CoverageConfig = _CoverageConfig

coverage.env.SYSMON_DEFAULT = False
