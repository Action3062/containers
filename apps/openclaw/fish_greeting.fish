function fish_greeting
    set_color green
    echo '  openclaw web shell'
    set_color normal
    echo
    echo '  Commands:'
    echo '    openclaw onboard     Guided setup for messaging integrations'
    echo '    openclaw agent       Talk to the assistant'
    echo '    claude               Anthropic Claude Code CLI'
    echo
    echo "  Gateway:  http://127.0.0.1:$OPENCLAW_GATEWAY_PORT/healthz"
    echo '  State:    /config (persistent volume)'
    echo
end
