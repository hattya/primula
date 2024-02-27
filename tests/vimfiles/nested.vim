function! Hop() abort
  function! Step() abort
    function! Jump() abort
      echo 'global'
    endfunction
    call Jump()
  endfunction
  call Step()
endfunction

call Hop()

function! s:hop() abort
  function! s:step() abort
    function! s:jump() abort
      echo 'script local'
    endfunction
    call s:jump()
  endfunction
  call s:step()
endfunction

call s:hop()

let s:dict = {}
function! s:dict.hop() abort dict
  function! s:dict.step() abort dict
    function! s:dict.jump() abort dict
      echo 'dict'
    endfunction
    call s:dict.jump()
  endfunction
  call s:dict.step()
endfunction

call s:dict.hop()
