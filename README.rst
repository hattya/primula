Primula
=======

Primula is a code coverage tool for `Vim script`_.

.. image:: https://img.shields.io/pypi/v/primula
   :target: https://pypi.org/project/primula

.. image:: https://github.com/hattya/primula/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/hattya/primula/actions/workflows/ci.yml

.. image:: https://ci.appveyor.com/api/projects/status/if338u3j55a8kekm?svg=true
   :target: https://ci.appveyor.com/project/hattya/primula

.. image:: https://codecov.io/gh/hattya/primula/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/hattya/primula

.. _Vim script: https://www.vim.org/


Installation
------------

.. code:: console

   $ pip install primula


Requirements
------------

- Python 3.9+
- coverage 5.0+
- Vim 7.4+


Usage
-----

run
~~~

.. code:: console

   $ primula run vim --clean -Nnu vimrc -S /path/to/script.vim -c q
   $ primula report -m

The contents of ``vimrc`` as follow:

.. code:: vim

   if $PROFILE !=# ''
     execute 'profile start' $PROFILE
     profile! file ./*
   endif


combine
~~~~~~~

.. code:: console

   $ vim --clean -Nn --cmd "profile start profile.txt" --cmd "profile! file ./*" -S /path/to/script.vim -c q
   $ primula combine profile.txt
   $ primula report -m


Configuration
-------------

.coveragerc
~~~~~~~~~~~

.. code:: ini

   [primula]
   environ = PROFILE
   profile = profile.txt


cond
  It controls whether following condition commands to be included as
  statements.

  - ``:elsei[f]``
  - ``:cat[ch]``
  - ``:fina[lly]``

  They are counted by Vim 8.1.309+.
  
  Default: ``True``

end
  It controls whether following end commands to be included as statements.

  - ``:en[dif]``
  - ``:endw[hile]``
  - ``:endfo[r]``
  - ``:endt[ry]``
  - ``:endf[unction]``

  Default: ``False``

environ
  An environment variable name.

  Default: ``PROFILE``

profile
  A profile output path.

  Default: ``profile.txt``


License
-------

Primula is distributed under the terms of the Apache License, Version 2.0.
