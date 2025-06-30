#
# test_cli
#
#   Copyright (c) 2024-2025 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

import contextlib
import io
import os
import re
import sys
import textwrap
import warnings

import coverage
import coverage.data

from primula import cli
from base import PrimulaTestCase


class CLITestCase(PrimulaTestCase):

    maxDiff = None

    def setUp(self):
        self._cwd = os.getcwd()
        self._dir = self.tempdir()
        self.root = self._dir.name
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self._cwd)
        self._dir.cleanup()

    def cli(self, *args):
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), \
             contextlib.redirect_stderr(err):
            try:
                cli.run(list(args))
            except SystemExit:
                pass
        return out.getvalue(), err.getvalue()

    def test_help(self):
        out, err = self.cli('help')
        v = out.splitlines()
        self.assertRegex(v[0], r'^Primula on coverage\.py version \S+')
        self.assertRegex(v[1], r'code coverage in Vim scripts\.$')
        self.assertEqual(err, '')

    def test_combine_no_data(self):
        out, err = self.cli('combine')
        self.assertRegex(out, r'(?i)no data to combine')
        self.assertEqual(err, '')

    def test_combine_data(self):
        path = '.coverage_combine'
        with open(path, 'w'):
            pass
        out, err = self.cli('combine', '.', path)
        if coverage.version_info >= (6, 3):
            self.assertRegex(out, re.escape(path))
            self.assertEqual(err, '')
        else:
            self.assertRegex(out, r'(?i)no usable data files')
            self.assertRegex(err, re.escape(path))

    def test_combine_profile(self):
        path = 'profile.txt'
        script = os.path.realpath('spam.vim')
        with open(path, 'w') as fp:
            fp.write(textwrap.dedent(f"""\
                SCRIPT  {script}
                Sourced 1 time
                Total time:   0.000000
                 Self time:   0.000000

                count  total (s)   self (s)
                    1              0.000000 function! If() abort
                                              echo 'if!'
                                            endfunction
                    1              0.000000 function! Else() abort
                                              echo 'else!'
                                            endfunction
                    1              0.000000 if 0
                                              call
                                              \\   If()
                    1              0.000000 else
                    1              0.000000   call
                                              \\   Else()
                    1              0.000000 endif

                FUNCTION  If()
                    Defined: {script}:1
                Called 1 time
                Total time:   0.000000
                 Self time:   0.000000

                count  total (s)   self (s)
                    1              0.000000   echo 'if!'

                FUNCTION  Else()
                    Defined: {script}:4
                Called 1 time
                Total time:   0.000000
                 Self time:   0.000000

                count  total (s)   self (s)
                    1              0.000000   echo 'else?'

                FUNCTIONS SORTED ON TOTAL TIME
            """))
            fp.flush()

        # branch = False
        out, err = self.cli('combine', path)
        self.assertEqual(out, '')
        self.assertRegex(err, r'(?i)could not find line for function: Else\(\)')

        data = coverage.data.CoverageData()
        data.read()
        self.assertEqual(data.measured_files(), {script})
        self.assertFalse(data.has_arcs())
        self.assertEqual(data.lines(script), [1, 2, 4, 7, 10, 11, 13])

        # branch = True
        warnings.resetwarnings()
        with open('.coveragerc', 'w') as fp:
            fp.write(textwrap.dedent("""\
                [run]
                branch = True
            """))

        out, err = self.cli('combine', path)
        self.assertEqual(out, '')
        self.assertRegex(err, r'(?i)could not find line for function: Else\(\)')

        data = coverage.data.CoverageData()
        data.read()
        self.assertEqual(data.measured_files(), {script})
        self.assertTrue(data.has_arcs())
        self.assertEqual(data.arcs(script), [(-1, 1), (1, 2), (3, 4), (6, 7), (8, 10), (10, 11), (11, 13), (13, -1)])

    def test_lcov(self):
        path = 'profile.txt'
        script = os.path.realpath('spam.vim')
        with open(path, 'w') as fp:
            fp.write(textwrap.dedent(f"""\
                SCRIPT  {script}
                Sourced 1 time
                Total time:   0.000000
                 Self time:   0.000000

                count  total (s)   self (s)
                   11              0.000000 for s:i in range(10)
                   10              0.000000   if s:i % 2 == 0
                    5              0.000000     echo 'even'
                    5              0.000000   else
                    5              0.000000     echo 'odd'
                   10              0.000000   endif
                   11              0.000000 endfor

                FUNCTIONS SORTED ON TOTAL TIME
            """))
            fp.flush()
        with open(script, 'w') as fp:
            fp.write(textwrap.dedent("""\
                for s:i in range(10)
                  if s:i % 2 == 0
                    echo 'even'
                  else
                    echo 'odd'
                  endif
                endfor
            """))
            fp.flush()

        out, err = self.cli('combine', path)
        self.assertEqual(out, '')
        self.assertEqual(err, '')

        out, err = self.cli('lcov')
        if coverage.version_info >= (6, 1):
            self.assertRegex(out, re.escape(cli._LCOV_OUTPUT))
        else:
            self.assertEqual(out, '')
        self.assertEqual(err, '')
        with open(cli._LCOV_OUTPUT) as fp:
            self.assertEqual(fp.read(), textwrap.dedent("""\
                TN:
                SF:spam.vim
                DA:1,11
                DA:2,10
                DA:3,5
                DA:4,5
                DA:5,5
                LF:5
                LH:5
                end_of_record
            """))

        os.unlink(path)

        out, err = self.cli('lcov')
        if coverage.version_info >= (6, 1):
            self.assertRegex(out, re.escape(cli._LCOV_OUTPUT))
        else:
            self.assertEqual(out, '')
        self.assertEqual(err, '')
        with open(cli._LCOV_OUTPUT) as fp:
            self.assertEqual(fp.read(), textwrap.dedent("""\
                TN:
                SF:spam.vim
                DA:1,1
                DA:2,1
                DA:3,1
                DA:4,1
                DA:5,1
                LF:5
                LH:5
                end_of_record
            """))

    def test_run_without_args(self):
        out, err = self.cli('run')
        self.assertNotEqual(out, '')
        self.assertRegex(err, r'(?i)nothing to do')

    def test_run_not_found(self):
        args = ['__primula.cli__']
        out, err = self.cli('run', *args)
        self.assertRegex(out, fr'(?i)could not find command: {args[0]}')
        self.assertEqual(err, '')

    def test_run(self):
        for environ, profile in (
            ('', ''),
            (cli._ENVIRON, cli._PROFILE),
            ('VIM_PROFILE', 'vim_profile.txt'),
        ):
            with self.subTest(environ=environ, profile=profile):
                with open('.coveragerc', 'w') as fp:
                    fp.write('[primula]\n')
                    if environ:
                        fp.write(f'environ = {environ}\n')
                    if profile:
                        fp.write(f'profile = {profile}\n')
                    fp.flush()

                profile = profile or cli._PROFILE
                script = os.path.realpath('spam.vim')
                with open(profile, 'w') as fp:
                    fp.write(textwrap.dedent(f"""\
                        SCRIPT  {script}
                        Sourced 1 time
                        Total time:   0.000000
                         Self time:   0.000000

                        count  total (s)   self (s)
                            1              0.000000 echo 'spam'

                        FUNCTIONS SORTED ON TOTAL TIME
                    """))
                    fp.flush()
                with open(script, 'w') as fp:
                    fp.write(textwrap.dedent("""\
                        echo 'spam'
                    """))
                    fp.flush()

                args = [sys.executable, '-c', '...']
                out, err = self.cli('run', *args)
                self.assertEqual(out, '')
                self.assertEqual(err, '')

                data = coverage.data.CoverageData()
                data.read()
                self.assertEqual(data.measured_files(), {script})
                self.assertFalse(data.has_arcs())
                self.assertEqual(data.lines(script), [1])

                os.unlink(profile)

    def test_run_with_append(self):
        with open('.coveragerc', 'w') as fp:
            fp.write(textwrap.dedent("""\
                [run]
                plugins = primula
            """))
            fp.flush()

        profile = 'profile.txt'
        scripts = [
            os.path.realpath('spam.vim'),
            os.path.realpath('eggs.vim'),
        ]
        with open(profile, 'w') as fp:
            fp.write(textwrap.dedent(f"""\
                SCRIPT  {scripts[0]}
                Sourced 1 time
                Total time:   0.000000
                 Self time:   0.000000

                count  total (s)   self (s)
                    1              0.000000 echo 'spam'

                FUNCTIONS SORTED ON TOTAL TIME
            """))
            fp.flush()
        with open(scripts[0], 'w') as fp:
            fp.write(textwrap.dedent("""\
                echo 'spam'
            """))
            fp.flush()

        args = [sys.executable, '-c', '...']
        out, err = self.cli('run', *args)
        self.assertEqual(out, '')
        self.assertEqual(err, '')

        data = coverage.data.CoverageData()
        data.read()
        self.assertEqual(data.measured_files(), set(scripts[:1]))
        self.assertFalse(data.has_arcs())
        self.assertEqual(data.lines(scripts[0]), [1])

        with open(profile, 'w') as fp:
            fp.write(textwrap.dedent(f"""\
                SCRIPT  {scripts[1]}
                Sourced 1 time
                Total time:   0.000000
                 Self time:   0.000000

                count  total (s)   self (s)
                    1              0.000000 echo 'eggs'

                FUNCTIONS SORTED ON TOTAL TIME
            """))
            fp.flush()
        with open(scripts[1], 'w') as fp:
            fp.write(textwrap.dedent("""\
                echo 'eggs'
            """))
            fp.flush()

        args = [sys.executable, '-c', '...']
        out, err = self.cli('run', '-a', *args)
        self.assertEqual(out, '')
        self.assertEqual(err, '')

        data = coverage.data.CoverageData()
        data.read()
        self.assertEqual(data.measured_files(), set(scripts))
        self.assertFalse(data.has_arcs())
        self.assertEqual(data.lines(scripts[0]), [1])
        self.assertEqual(data.lines(scripts[1]), [1])
