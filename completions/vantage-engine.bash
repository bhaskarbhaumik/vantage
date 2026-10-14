_vantage_engine_completion() {
    local IFS=$'
'
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _VANTAGE_ENGINE_COMPLETE=complete_bash $1 ) )
    return 0
}

complete -o default -F _vantage_engine_completion vantage-engine
