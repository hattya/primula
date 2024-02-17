#! /usr/bin/env python
#
# profile
#
#   Copyright (c) 2024 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

import os
from pathlib import Path
import subprocess
import sys
import urllib.request
import zipfile

import click


ROOT = Path(__file__).parent.parent
TESTS = ROOT / 'tests'
BUILD = ROOT / 'build'


@click.command
@click.option('-v', '--verbose', is_flag=True,
              help='Show verbose information.')
@click.pass_context
def profile(ctx: click.Context, verbose: bool) -> None:
    """Update Vim profile outputs."""

    profiles = TESTS / 'profiles'
    vimfiles = TESTS / 'vimfiles'
    profiles.mkdir(parents=True, exist_ok=True)

    for tag, version in (
        ('v9.0.0000', '9.0.0000'),
    ):
        try:
            vim = setup_vim(version, verbose=verbose)
            if verbose:
                click.echo(f'>> profile with Vim {version}')
            for path in vimfiles.iterdir():
                if path.suffix != '.vim':
                    continue
                profile = profiles / f'{path.stem}.{tag}.txt'
                os.environ['PROFILE'] = str(profile)
                subprocess.run((vim, '--clean', '-Nensu', vimfiles / 'vimrc',  '-S', path, '-c', 'q'), check=True)
                rel_script(profile)
        except subprocess.CalledProcessError as e:
            ctx.exit(e.returncode)


def setup_vim(version: str, verbose: bool = False) -> Path:
    root = BUILD / f'vim-{version}'
    root.mkdir(parents=True, exist_ok=True)

    if sys.platform == 'win32':
        repo = 'https://github.com/vim/vim-win32-installer'
        path = root / 'vim.zip'
        vim = root / 'vim' / f'vim{"".join(version.split(".")[:2])}' / 'vim.exe'
        # fetch
        if not path.exists():
            if verbose:
                click.echo(f'>> fetch Vim {version}')
            with urllib.request.urlopen(f'{repo}/releases/download/v{version}/gvim_{version}_x64.zip') as resp, \
                 path.open('wb') as fp:
                fp.write(resp.read())
        # unpack
        if not vim.exists():
            if verbose:
                click.echo(f'>> unpack Vim {version}')
            with zipfile.ZipFile(path) as zf:
                zf.extractall(path=root)
        return vim
    elif sys.platform.startswith('linux'):
        repo = 'https://github.com/vim/vim'
        vim = root / 'src' / 'vim'
        # clone
        if not (root / '.git').exists():
            if verbose:
                click.echo(f'>> clone Vim {version}')
            subprocess.run(('git', '-c', 'advice.detachedHead=false', 'clone', '-b', f'v{version}', '--depth', '1', repo, root), check=True)
        # build
        if not vim.exists():
            if verbose:
                click.echo(f'>> build Vim {version}')
            subprocess.run(('./configure', '--enable-gui=no', '--disable-nls'), check=True, cwd=root)
            subprocess.run(('make', '-j', str(os.cpu_count() + 1)), check=True, cwd=root)
        os.environ['VIMRUNTIME'] = os.path.join(root, 'runtime')
        return vim
    raise Exception(f'cannot setup Vim {version}')


def rel_script(path: Path) -> None:
    kwds = ('SCRIPT ', '    Defined:')
    root = os.path.join('tests', 'vimfiles')
    data = []
    with path.open(encoding='utf-8') as fp:
        for l in fp:
            if l.startswith(kwds):
                l = f'{kwds[0 if l[:4].strip() else 1]} {l[l.rindex(root):].replace(os.path.sep, "/")}'
            data.append(l)
    with path.open('w', encoding='utf-8', newline='') as fp:
        fp.writelines(data)


if __name__ == '__main__':
    profile()
