#!/usr/bin/env bash
# Drops the user into a restricted tmux session running fish.
# Used both as ttyd's command and as the `shell` entrypoint mode.

set -euo pipefail

session="openclaw"

# Attach if a session already exists, otherwise create one.
if tmux -f /restricted.tmux.conf has-session -t "${session}" 2>/dev/null; then
  exec tmux -f /restricted.tmux.conf attach-session -t "${session}"
fi

exec tmux -f /restricted.tmux.conf new-session -s "${session}" -A /usr/bin/fish --login
