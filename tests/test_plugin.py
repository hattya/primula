#
# test_plugin
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

import os
import textwrap

import coverage.config
import coverage.plugin_support

from primula import plugin
from base import PrimulaTestCase


class PluginTestCase(PrimulaTestCase):

    maxDiff = None

    def setUp(self):
        self._cwd = os.getcwd()
        self._dir = self.tempdir()
        self.root = self._dir.name
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self._cwd)
        self._dir.cleanup()

    def test_coverage_init(self):
        plugins = coverage.plugin_support.Plugins.load_plugins(['primula'], coverage.config.CoverageConfig(), False)
        self.assertEqual(list(plugins.names), ['primula.VimScriptPlugin'])

    def test_to_bool(self):
        self.assertTrue(plugin._to_bool(None, True))
        self.assertTrue(plugin._to_bool(' ', False))

        self.assertFalse(plugin._to_bool())
        self.assertFalse(plugin._to_bool(None, False))
        for s in ('', '0', 'False', 'no', 'off'):
            self.assertFalse(plugin._to_bool(s, True))

    def test_find_executable_files(self):
        os.mkdir('autoload')
        with open('spam.vim', 'w'):
            pass
        with open(os.path.join('autoload', 'eggs.vim'), 'w'):
            pass
        with open('ham.txt', 'w'):
            pass

        p = plugin.VimScriptPlugin(cond=True, end=False)
        self.assertEqual(list(p.find_executable_files(self.root)), [
            os.path.join(self.root, 'spam.vim'),
            os.path.join(self.root, 'autoload', 'eggs.vim'),
        ])

    def test_file_reporter(self):
        path = os.path.join(self.root, 'spam.vim')
        source = textwrap.dedent("""\
            echo 0
            \\ 1
            if 0
              echo 'if'
            elseif 1
              echo 'elseif 1'
            elseif 2
              echo 'elseif 2'
            endif
        """)
        with open(path, 'w') as fp:
            fp.write(source)
            fp.flush()

        for cond, end, lines in (
            (False, False, set((1, 3, 4, 6, 8))),
            (False, True, set((1, 3, 4, 6, 8, 9))),
            (True, False, set((1, 3, 4, 5, 6, 7, 8))),
            (True, True, set((1, 3, 4, 5, 6, 7, 8, 9))),
        ):
            with self.subTest(cond=cond, end=end):
                p = plugin.VimScriptPlugin(cond=cond, end=end)
                fr = p.file_reporter(path)
                self.assertEqual(fr.source(), source)
                self.assertEqual(fr.lines(), lines)
