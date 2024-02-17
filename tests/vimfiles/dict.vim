let s:dict = {}

function! s:dict.today() abort dict
  echo strftime('%Y-%m-%d')
endfunction

function! s:dict.main() abort dict
  echo 'Hello, world!'
endfunction

call s:dict.main()
