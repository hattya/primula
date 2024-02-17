let s:save_cpo = &cpo
set cpo&vim

function! autoload#today() abort
  echo strftime('%Y-%m-%d')
endfunction

function! autoload#main() abort
  echo 'Hello, world!'
endfunction

let &cpo = s:save_cpo
unlet s:save_cpo
