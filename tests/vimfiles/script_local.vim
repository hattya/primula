function! s:today() abort
  echo strftime('%Y-%m-%d')
endfunction

function! s:main() abort
  echo 'Hello, world!'
endfunction

call s:main()
