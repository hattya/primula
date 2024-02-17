function! Today() abort
  echo strftime('%Y-%m-%d')
endfunction

function! Main() abort
  echo 'Hello, world!'
endfunction

call Main()
