#
# test_lcov
#
#   Copyright (c) 2025 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

import io
import os
import textwrap

import coverage.cmdline
import coverage.files

from primula import cli, core, lcov
from base import PrimulaTestCase


class LCOVTestCase(PrimulaTestCase):

    maxDiff = None

    def setUp(self):
        self._cwd = os.getcwd()
        self._dir = self.tempdir()
        self.root = self._dir.name
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self._cwd)
        self._dir.cleanup()

    def test_options(self):
        Opts = coverage.cmdline.Opts
        parser = (coverage.cmdline.COMMANDS if coverage.version_info >= (6, 3) else coverage.cmdline.CMDS)['lcov']

        if coverage.version_info >= (7, 3, 3):
            self.assertTrue(parser.has_option(Opts.datafle_input.get_opt_string()))
        elif coverage.version_info >= (6, 3):
            self.assertTrue(parser.has_option(Opts.input_datafile.get_opt_string()))
        self.assertTrue(parser.has_option(Opts.fail_under.get_opt_string()))
        self.assertTrue(parser.has_option(Opts.ignore_errors.get_opt_string()))
        self.assertTrue(parser.has_option(Opts.include.get_opt_string()))
        self.assertTrue(parser.has_option(Opts.omit.get_opt_string()))
        self.assertTrue(parser.has_option(Opts.output_lcov.get_opt_string()))
        if coverage.version_info >= (6, 1):
            self.assertTrue(parser.has_option(Opts.quiet.get_opt_string()))

    def test_report(self):
        path = 'profile.txt'
        script = coverage.files.abs_file('spam.vim')
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

        c = cli._Coverage()
        c.combine([path])

        r = lcov.LCOVReporter(c, core.Profile(path))
        out = io.StringIO()
        self.assertEqual(r.report(None, out), 100.0)
        self.assertEqual(out.getvalue(), textwrap.dedent("""\
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

        r = lcov.LCOVReporter(c, None)
        out = io.StringIO()
        self.assertEqual(r.report(None, out), 100.0)
        self.assertEqual(out.getvalue(), textwrap.dedent("""\
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
