execute "function! Spam() abort\n  echo 1\nendfunction"
execute join([
\         'function! Eggs() abort',
\         '  echo 2',
\         'endfunction',
\       ], "\n")

call Spam()
call Eggs()

function! Define(name, v) abort
  execute "function! " . a:name . "() abort\n  echo " . a:v . "\nendfunction"
endfunction

call Define('Ham', 3)
call Define('Toast', 4)

call Ham()
call Toast()

execute join([
\         'function! Beans() abort',
\         '  echo 5',
\         'endfunction',
\       ], "\n")
