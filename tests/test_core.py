#
# test_core
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

import contextlib
import os
import tempfile
import textwrap
import unittest

import primula
from primula import core


class CoreTestCase(unittest.TestCase):

    maxDiff = None
    tags = [
        'v9.0.1411',
        'v9.0.0000',
    ]

    def profile(self, name):
        return os.path.join(os.path.dirname(__file__), 'profiles', name)

    @contextlib.contextmanager
    def tempfile(self):
        fd, path = tempfile.mkstemp(prefix='primula-')
        try:
            os.close(fd)
            yield path
        finally:
            os.unlink(path)

    def lines(self, o):
        return [(l.count or 0, l.line) for l in o.lines]

    def test_global(self):
        for tag in self.tags:
            with self.subTest(tag=tag):
                p = core.Profile(self.profile(f'global.{tag}.txt'))
                self.assertEqual(len(p.scripts), 1)
                self.assertEqual(len(p.functions), 2)

                path = 'tests/vimfiles/global.vim'
                s = p.scripts[path]
                self.assertEqual(s.path, path)
                self.assertEqual(s.sourced, 1)
                self.assertGreater(s.total_time, 0.0)
                self.assertGreater(s.self_time, 0.0)
                self.assertEqual(self.lines(s), [
                    (1, 'function! Today() abort'),
                    (0, "  echo strftime('%Y-%m-%d')"),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'function! Main() abort'),
                    (1, "  echo 'Hello, world!'"),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'call Main()'),
                ])

                f = p.functions[0]
                self.assertEqual(f.name, 'Today()')
                self.assertEqual(f.defined, (path, 1))
                self.assertEqual(f.called, 0)
                self.assertEqual(f.total_time, 0.0)
                self.assertEqual(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (0, "  echo strftime('%Y-%m-%d')"),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[1]
                self.assertEqual(f.name, 'Main()')
                self.assertEqual(f.defined, (path, 5))
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, "  echo 'Hello, world!'"),
                ])
                self.assertTrue(f.mapped)

    def test_script_local(self):
        for tag in self.tags:
            with self.subTest(tag=tag):
                p = core.Profile(self.profile(f'script_local.{tag}.txt'))
                self.assertEqual(len(p.scripts), 1)
                self.assertEqual(len(p.functions), 2)

                path = 'tests/vimfiles/script_local.vim'
                s = p.scripts[path]
                self.assertEqual(s.path, path)
                self.assertEqual(s.sourced, 1)
                self.assertGreater(s.total_time, 0.0)
                self.assertGreater(s.self_time, 0.0)
                self.assertEqual(self.lines(s), [
                    (1, 'function! s:today() abort'),
                    (0, "  echo strftime('%Y-%m-%d')"),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'function! s:main() abort'),
                    (1, "  echo 'Hello, world!'"),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'call s:main()'),
                ])

                f = p.functions[1]
                self.assertEqual(f.name, '<SNR>2_today()')
                self.assertEqual(f.defined, (path, 1))
                self.assertEqual(f.called, 0)
                self.assertEqual(f.total_time, 0.0)
                self.assertEqual(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (0, "  echo strftime('%Y-%m-%d')"),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[0]
                self.assertEqual(f.name, '<SNR>2_main()')
                self.assertEqual(f.defined, (path, 5))
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, "  echo 'Hello, world!'"),
                ])
                self.assertTrue(f.mapped)

    def test_dict(self):
        for tag in self.tags:
            with self.subTest(tag=tag):
                p = core.Profile(self.profile(f'dict.{tag}.txt'))
                self.assertEqual(len(p.scripts), 1)
                self.assertEqual(len(p.functions), 2)

                path = 'tests/vimfiles/dict.vim'
                s = p.scripts[path]
                self.assertEqual(s.path, path)
                self.assertEqual(s.sourced, 1)
                self.assertGreater(s.total_time, 0.0)
                self.assertGreater(s.self_time, 0.0)
                self.assertEqual(self.lines(s), [
                    (1, 'let s:dict = {}'),
                    (0, ''),
                    (1, 'function! s:dict.today() abort dict'),
                    (0, "  echo strftime('%Y-%m-%d')"),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'function! s:dict.main() abort dict'),
                    (1, "  echo 'Hello, world!'"),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'call s:dict.main()'),
                ])

                f = p.functions[0]
                self.assertEqual(f.name, '1()')
                self.assertEqual(f.defined, (path, 3))
                self.assertEqual(f.called, 0)
                self.assertEqual(f.total_time, 0.0)
                self.assertEqual(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (0, "  echo strftime('%Y-%m-%d')"),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[1]
                self.assertEqual(f.name, '2()')
                self.assertEqual(f.defined, (path, 7))
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, "  echo 'Hello, world!'"),
                ])
                self.assertTrue(f.mapped)

    def test_autoload(self):
        for tag in self.tags:
            with self.subTest(tag=tag):
                p = core.Profile(self.profile(f'autoload.{tag}.txt'))
                self.assertEqual(len(p.scripts), 2)
                self.assertEqual(len(p.functions), 2)

                path = 'tests/vimfiles/autoload.vim'
                s = p.scripts[path]
                self.assertEqual(s.path, path)
                self.assertEqual(s.sourced, 1)
                self.assertGreater(s.total_time, 0.0)
                self.assertGreater(s.self_time, 0.0)
                self.assertEqual(self.lines(s), [
                    (1, 'call autoload#main()'),
                ])

                path = 'tests/vimfiles/autoload/autoload.vim'
                s = p.scripts[path]
                self.assertEqual(s.path, path)
                self.assertEqual(s.sourced, 1)
                self.assertGreater(s.total_time, 0.0)
                self.assertGreater(s.self_time, 0.0)
                self.assertEqual(self.lines(s), [
                    (1, 'let s:save_cpo = &cpo'),
                    (1, 'set cpo&vim'),
                    (0, ''),
                    (1, 'function! autoload#today() abort'),
                    (0, "  echo strftime('%Y-%m-%d')"),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'function! autoload#main() abort'),
                    (1, "  echo 'Hello, world!'"),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'let &cpo = s:save_cpo'),
                    (1, 'unlet s:save_cpo'),
                ])

                f = p.functions[0]
                self.assertEqual(f.name, 'autoload#today()')
                self.assertEqual(f.defined, (path, 4))
                self.assertEqual(f.called, 0)
                self.assertEqual(f.total_time, 0.0)
                self.assertEqual(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (0, "  echo strftime('%Y-%m-%d')"),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[1]
                self.assertEqual(f.name, 'autoload#main()')
                self.assertEqual(f.defined, (path, 8))
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, "  echo 'Hello, world!'"),
                ])
                self.assertTrue(f.mapped)

    def test_function_line_mismatch(self):
        with self.tempfile() as path:
            script = 'tests/vimfiles/line_mismatch.vim'
            with open(path, 'w') as fp:
                fp.write(textwrap.dedent(f"""\
                    SCRIPT  {script}
                    Sourced 1 time
                    Total time:   0.000000
                     Self time:   0.000000

                    count  total (s)   self (s)
                        1              0.000000 function! Main() abort
                                                  echo '============='
                                                  echo 'Hello, world!'
                                                  echo '============='
                                                endfunction
                        1   0.000000   0.000000 call Main()

                    FUNCTION  Main()
                        Defined: {script}:1
                    Called 1 time
                    Total time:   0.000000
                     Self time:   0.000000

                    count  total (s)   self (s)
                        1              0.000000   echo '============='
                        1              0.000000   echo 'Hello, world?'
                        1              0.000000   echo '============='

                    FUNCTIONS SORTED ON TOTAL TIME
                """))
                fp.flush()

            p = core.Profile(path)
            self.assertEqual(len(p.scripts), 1)
            self.assertEqual(len(p.functions), 1)

            s = p.scripts[script]
            self.assertEqual(self.lines(s), [
                (1, 'function! Main() abort'),
                (0, "  echo '============='"),
                (0, "  echo 'Hello, world!'"),
                (0, "  echo '============='"),
                (0, 'endfunction'),
                (1, 'call Main()'),
            ])

            f = p.functions[0]
            self.assertEqual(self.lines(f), [
                (1, "  echo '============='"),
                (1, "  echo 'Hello, world?'"),
                (1, "  echo '============='"),
            ])
            self.assertFalse(f.mapped)

    def test_parse_error(self):
        with self.tempfile() as path:
            # unexpected line
            with open(path, 'w') as fp:
                fp.write(textwrap.dedent("""\
                    ....
                """))
                fp.flush()
            with self.assertRaises(primula.ProfileError) as cm:
                core.Profile(path)
            self.assertEqual(str(cm.exception), 'unexpected line')

            # cannot parse SCRIPT
            with open(path, 'w') as fp:
                fp.write(textwrap.dedent("""\
                    SCRIPT  ...
                    ....
                """))
                fp.flush()
            with self.assertRaises(primula.ProfileError) as cm:
                core.Profile(path)
            self.assertEqual(str(cm.exception), 'cannot parse SCRIPT')

            # cannot parse FUNCTION
            with open(path, 'w') as fp:
                fp.write(textwrap.dedent("""\
                    SCRIPT  ...
                    Sourced 0 time
                    Total time:   0.000000
                     Self time:   0.000000

                    count  total (s)   self (s)

                    FUNCTION  ...
                    ....
                """))
                fp.flush()
            with self.assertRaises(primula.ProfileError) as cm:
                core.Profile(path)
            self.assertEqual(str(cm.exception), 'cannot parse FUNCTION')
