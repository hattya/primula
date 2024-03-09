#
# test_core
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

import os
import textwrap

import primula
from primula import core
from base import PrimulaTestCase


class CoreTestCase(PrimulaTestCase):

    maxDiff = None
    tags = [
        'v9.0.1411',
        'v9.0.0000',
        'v8.1.0365',
        'v7.4',
    ]

    def profile(self, name):
        return os.path.join(os.path.dirname(__file__), 'profiles', name)

    def lines(self, o):
        return [(l.count or 0, l.line) for l in o.lines]

    def version_info(self, tag):
        return tuple(map(int, tag.lstrip('v').split('.')))

    def test_global(self):
        for tag in self.tags:
            with self.subTest(tag=tag):
                version_info = self.version_info(tag)

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
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 1))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 0)
                self.assertEqual(f.total_time, 0.0)
                self.assertEqual(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (0, "  echo strftime('%Y-%m-%d')"),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[1]
                self.assertEqual(f.name, 'Main()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 5))
                else:
                    self.assertIsNone(f.defined)
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
                version_info = self.version_info(tag)

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
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 1))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 0)
                self.assertEqual(f.total_time, 0.0)
                self.assertEqual(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (0, "  echo strftime('%Y-%m-%d')"),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[0]
                self.assertEqual(f.name, '<SNR>2_main()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 5))
                else:
                    self.assertIsNone(f.defined)
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
                version_info = self.version_info(tag)

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
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 3))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 0)
                self.assertEqual(f.total_time, 0.0)
                self.assertEqual(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (0, "  echo strftime('%Y-%m-%d')"),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[1]
                self.assertEqual(f.name, '2()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 7))
                else:
                    self.assertIsNone(f.defined)
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
                version_info = self.version_info(tag)

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
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 4))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 0)
                self.assertEqual(f.total_time, 0.0)
                self.assertEqual(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (0, "  echo strftime('%Y-%m-%d')"),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[1]
                self.assertEqual(f.name, 'autoload#main()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 8))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, "  echo 'Hello, world!'"),
                ])
                self.assertTrue(f.mapped)

    def test_line_continuation(self):
        for tag in self.tags:
            with self.subTest(tag=tag):
                version_info = self.version_info(tag)

                p = core.Profile(self.profile(f'line_continuation.{tag}.txt'))
                self.assertEqual(len(p.scripts), 1)
                self.assertEqual(len(p.functions), 1)

                path = 'tests/vimfiles/line_continuation.vim'
                s = p.scripts[path]
                self.assertEqual(s.path, path)
                self.assertEqual(s.sourced, 1)
                self.assertGreater(s.total_time, 0.0)
                self.assertGreater(s.self_time, 0.0)
                self.assertEqual(self.lines(s), [
                    (1, 'function! Echo() abort'),
                    (1, '  echo 0'),
                    (1, '  \\ 1'),
                    (1, '  echo 2'),
                    (1, '  \\  3'),
                    (1, '  \\ 4'),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'call Echo()'),
                    (1, 'echo 5'),
                    (1, '\\ 6'),
                    (1, 'echo 7'),
                    (1, '\\  8'),
                    (1, '\\ 9'),
                ])

                f = p.functions[0]
                self.assertEqual(f.name, 'Echo()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 1))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, "  echo 0 1"),
                    (1, "  echo 2  3 4"),
                ])
                self.assertTrue(f.mapped)

    def test_execute(self):
        for tag in self.tags:
            with self.subTest(tag=tag):
                version_info = self.version_info(tag)

                p = core.Profile(self.profile(f'execute.{tag}.txt'))
                self.assertEqual(len(p.scripts), 1)
                self.assertEqual(len(p.functions), 6)

                path = 'tests/vimfiles/execute.vim'
                s = p.scripts[path]
                self.assertEqual(s.path, path)
                self.assertEqual(s.sourced, 1)
                self.assertGreater(s.total_time, 0.0)
                self.assertGreater(s.self_time, 0.0)
                self.assertEqual(self.lines(s), [
                    (1, r'execute "function! Spam() abort\n  echo 1\nendfunction"'),
                    (1, r'execute join(['),
                    (1, r"\         'function! Eggs() abort',"),
                    (1, r"\         '  echo 2',"),
                    (1, r"\         'endfunction',"),
                    (1, r'\       ], "\n")'),
                    (0, r''),
                    (1, r'call Spam()'),
                    (1, r'call Eggs()'),
                    (0, r''),
                    (1, r'function! Define(name, v) abort'),
                    (2, r'  execute "function! " . a:name . "() abort\n  echo " . a:v . "\nendfunction"'),
                    (0, r'endfunction'),
                    (0, r''),
                    (1, r"call Define('Ham', 3)"),
                    (1, r"call Define('Toast', 4)"),
                    (0, r''),
                    (1, r'call Ham()'),
                    (1, r'call Toast()'),
                    (0, r''),
                    (1, r'execute join(['),
                    (1, r"\         'function! Beans() abort',"),
                    (1, r"\         '  echo 5',"),
                    (1, r"\         'endfunction',"),
                    (1, r'\       ], "\n")'),
                ])

                f = p.functions[4]
                self.assertEqual(f.name, 'Spam()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 1))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, '  echo 1'),
                ])
                self.assertFalse(f.mapped)

                f = p.functions[3]
                self.assertEqual(f.name, 'Eggs()')
                if version_info >= (8, 1, 1625):
                    self.assertEqual(f.defined, (path, 2))
                elif version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 4))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, '  echo 2'),
                ])
                self.assertFalse(f.mapped)

                f = p.functions[1]
                self.assertEqual(f.name, 'Define()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 11))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 2)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (2, r'  execute "function! " . a:name . "() abort\n  echo " . a:v . "\nendfunction"'),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[5]
                self.assertEqual(f.name, 'Ham()')
                if version_info >= (8, 1, 1625):
                    self.assertEqual(f.defined, (path, 12))
                elif version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 10))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, '  echo 3'),
                ])
                self.assertFalse(f.mapped)

                f = p.functions[0]
                self.assertEqual(f.name, 'Toast()')
                if version_info >= (8, 1, 1625):
                    self.assertEqual(f.defined, (path, 12))
                elif version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 10))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, '  echo 4'),
                ])
                self.assertFalse(f.mapped)

                f = p.functions[2]
                self.assertEqual(f.name, 'Beans()')
                if version_info >= (8, 1, 1625):
                    self.assertEqual(f.defined, (path, 21))
                elif version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 23))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 0)
                self.assertEqual(f.total_time, 0.0)
                self.assertEqual(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (0, '  echo 5'),
                ])
                self.assertFalse(f.mapped)

    def test_duplicate(self):
        for tag in self.tags:
            with self.subTest(tag=tag):
                version_info = self.version_info(tag)
                c = 1 if version_info >= (8, 1, 365) else 0

                p = core.Profile(self.profile(f'duplicate.{tag}.txt'))
                self.assertEqual(len(p.scripts), 1)
                self.assertEqual(len(p.functions), 2)

                path = 'tests/vimfiles/duplicate.vim'
                s = p.scripts[path]
                self.assertEqual(s.path, path)
                self.assertEqual(s.sourced, 1)
                self.assertGreater(s.total_time, 0.0)
                self.assertGreater(s.self_time, 0.0)
                self.assertEqual(self.lines(s), [
                    (1, 'function! Spam(...) abort'),
                    (c, '  return a:000'),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'function! Eggs(...) abort'),
                    (0, '  return a:000'),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'call Spam()'),
                ])

                f = p.functions[1]
                self.assertEqual(f.name, 'Spam()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 1))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, '  return a:000'),
                ])
                if version_info >= (8, 1, 365):
                    self.assertTrue(f.mapped)
                else:
                    self.assertFalse(f.mapped)

                f = p.functions[0]
                self.assertEqual(f.name, 'Eggs()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 5))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 0)
                self.assertEqual(f.total_time, 0.0)
                self.assertEqual(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (0, '  return a:000'),
                ])
                if version_info >= (8, 1, 365):
                    self.assertTrue(f.mapped)
                else:
                    self.assertFalse(f.mapped)

    def test_nested(self):
        for tag in self.tags:
            with self.subTest(tag=tag):
                version_info = self.version_info(tag)

                p = core.Profile(self.profile(f'nested.{tag}.txt'))
                self.assertEqual(len(p.scripts), 1)
                self.assertEqual(len(p.functions), 9)

                path = 'tests/vimfiles/nested.vim'
                s = p.scripts[path]
                self.assertEqual(s.path, path)
                self.assertEqual(s.sourced, 1)
                self.assertGreater(s.total_time, 0.0)
                self.assertGreater(s.self_time, 0.0)
                self.assertEqual(self.lines(s), [
                    (1, 'function! Hop() abort'),
                    (1, '  function! Step() abort'),
                    (1, '    function! Jump() abort'),
                    (1, "      echo 'global'"),
                    (0, '    endfunction'),
                    (1, '    call Jump()'),
                    (0, '  endfunction'),
                    (1, '  call Step()'),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'call Hop()'),
                    (0, ''),
                    (1, 'function! s:hop() abort'),
                    (1, '  function! s:step() abort'),
                    (1, '    function! s:jump() abort'),
                    (1, "      echo 'script local'"),
                    (0, '    endfunction'),
                    (1, '    call s:jump()'),
                    (0, '  endfunction'),
                    (1, '  call s:step()'),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'call s:hop()'),
                    (0, ''),
                    (1, 'let s:dict = {}'),
                    (1, 'function! s:dict.hop() abort dict'),
                    (1, '  function! s:dict.step() abort dict'),
                    (1, '    function! s:dict.jump() abort dict'),
                    (1, "      echo 'dict'"),
                    (0, '    endfunction'),
                    (1, '    call s:dict.jump()'),
                    (0, '  endfunction'),
                    (1, '  call s:dict.step()'),
                    (0, 'endfunction'),
                    (0, ''),
                    (1, 'call s:dict.hop()'),
                ])

                f = p.functions[3]
                self.assertEqual(f.name, 'Hop()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 1))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, '  function! Step() abort'),
                    (1, '    function! Jump() abort'),
                    (1, "      echo 'global'"),
                    (0, '    endfunction'),
                    (1, '    call Jump()'),
                    (0, '  endfunction'),
                    (1, '  call Step()'),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[4]
                self.assertEqual(f.name, 'Step()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 2))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, '    function! Jump() abort'),
                    (1, "      echo 'global'"),
                    (0, '    endfunction'),
                    (1, '    call Jump()'),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[0]
                self.assertEqual(f.name, 'Jump()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 3))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, "      echo 'global'"),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[6]
                self.assertEqual(f.name, '<SNR>2_hop()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 13))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, '  function! s:step() abort'),
                    (1, '    function! s:jump() abort'),
                    (1, "      echo 'script local'"),
                    (0, '    endfunction'),
                    (1, '    call s:jump()'),
                    (0, '  endfunction'),
                    (1, '  call s:step()'),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[7]
                self.assertEqual(f.name, '<SNR>2_step()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 14))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, '    function! s:jump() abort'),
                    (1, "      echo 'script local'"),
                    (0, '    endfunction'),
                    (1, '    call s:jump()'),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[8]
                self.assertEqual(f.name, '<SNR>2_jump()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 15))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, "      echo 'script local'"),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[1]
                self.assertEqual(f.name, '1()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 26))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, '  function! s:dict.step() abort dict'),
                    (1, '    function! s:dict.jump() abort dict'),
                    (1, "      echo 'dict'"),
                    (0, '    endfunction'),
                    (1, '    call s:dict.jump()'),
                    (0, '  endfunction'),
                    (1, '  call s:dict.step()'),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[2]
                self.assertEqual(f.name, '2()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 27))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, '    function! s:dict.jump() abort dict'),
                    (1, "      echo 'dict'"),
                    (0, '    endfunction'),
                    (1, '    call s:dict.jump()'),
                ])
                self.assertTrue(f.mapped)

                f = p.functions[5]
                self.assertEqual(f.name, '3()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 28))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, "      echo 'dict'"),
                ])
                self.assertTrue(f.mapped)

    def test_lambda_expression(self):
        for tag in self.tags:
            with self.subTest(tag=tag):
                version_info = self.version_info(tag)

                if version_info < (7, 4, 2044):
                    continue

                p = core.Profile(self.profile(f'lambda.{tag}.txt'))
                self.assertEqual(len(p.scripts), 1)
                self.assertEqual(len(p.functions), 1)

                path = 'tests/vimfiles/lambda.vim'
                s = p.scripts[path]
                self.assertEqual(s.path, path)
                self.assertEqual(s.sourced, 1)
                self.assertGreater(s.total_time, 0.0)
                self.assertGreater(s.self_time, 0.0)
                self.assertEqual(self.lines(s), [
                    (1, "let Lambda = {-> 'Hello, world!'}"),
                    (1, 'echo Lambda()'),
                ])

                f = p.functions[0]
                self.assertEqual(f.name, '<lambda>1()')
                if version_info >= (8, 1, 365):
                    self.assertEqual(f.defined, (path, 1))
                else:
                    self.assertIsNone(f.defined)
                self.assertEqual(f.called, 1)
                self.assertGreater(f.total_time, 0.0)
                self.assertGreater(f.self_time, 0.0)
                self.assertEqual(self.lines(f), [
                    (1, "return 'Hello, world!'"),
                ])
                self.assertFalse(f.mapped)

    def test_script_line_mismatch(self):
        with self.tempdir() as root:
            path = os.path.join(root, 'profile.txt')
            script = os.path.join(root, 'line_mismatch.vim')
            with open(path, 'w') as fp:
                fp.write(textwrap.dedent(f"""\
                    SCRIPT  {script}
                    Sourced 1 time
                    Total time:   0.000000
                     Self time:   0.000000

                    count  total (s)   self (s)
                                                echo 0
                        1   0.000000   0.000000 echo 1

                    FUNCTIONS SORTED ON TOTAL TIME
                """))
                fp.flush()

            for data in (
                """\
                    echo 1
                    echo 2
                    \\   3
                """,
                """\
                    echo 0
                    echo 1
                    \\   2
                    echo 3
                    \\   4
                """,
            ):
                with open(script, 'w') as fp:
                    fp.write(textwrap.dedent(data))
                    fp.flush()

                p = core.Profile(path)
                self.assertEqual(len(p.scripts), 1)
                self.assertEqual(len(p.functions), 0)

                s = p.scripts[script]
                self.assertEqual(self.lines(s), [
                    (1, 'echo 0'),
                    (1, 'echo 1'),
                ])

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
