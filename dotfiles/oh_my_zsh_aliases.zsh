# This file must be placed in ~/.oh_my_zsh/custom

##### ----- Display ----- #####
alias ll='ls -alhF'
alias les="less -S"
alias zgrep='zgrep --color=auto'

##### ----- Utilities ----- #####
alias pbcopy="xclip -selection clipboard"
alias pbpaste="xclip -selection clipboard -o"
alias ccd="pwd | pbcopy"
alias dus="du -sh * | sort -hr"
alias c="code ."
#alias today="date +%F"
alias today='date +%Y%m%d'
alias open='xdg-open'

##### ----- Bioinfo ----- #####
alias grepfasta="grep -c '>'"
