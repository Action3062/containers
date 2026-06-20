# Environment for interactive fish sessions inside the openclaw container.
# Sourced automatically (conf.d/*.fish) before fish_greeting runs.

set -gx HOME /config
set -gx XDG_CONFIG_HOME /config
set -gx XDG_DATA_HOME /config/.local/share
set -gx LANG en_US.UTF-8
set -gx LC_ALL en_US.UTF-8

set -gx OPENCLAW_GATEWAY_PORT $OPENCLAW_GATEWAY_PORT
test -z "$OPENCLAW_GATEWAY_PORT"; and set -gx OPENCLAW_GATEWAY_PORT 18789

# Prepend the standard tooling paths idempotently.
for dir in /opt/bun/bin /home/linuxbrew/.linuxbrew/bin /home/linuxbrew/.linuxbrew/sbin /usr/local/bin
    if test -d "$dir"; and not contains -- "$dir" $PATH
        set -gx PATH $dir $PATH
    end
end
