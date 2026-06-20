#!/usr/bin/env bash
# Top-level dispatcher for the openclaw container.
#
# Modes (first CMD arg):
#   gateway   - run the OpenClaw gateway (default), optionally with ttyd web shell
#   shell     - drop into a restricted tmux + fish session (used by ttyd)
#   raw       - bypass wrappers and exec the rest of argv as-is (debug)
#
# Persistent state lives under $HOME (=/config) so a single PVC is enough.

set -euo pipefail

mode="${1:-gateway}"
shift || true

# Make sure customer-mounted /config always has the expected layout.
install -d -m 0755 \
  "${HOME}/.openclaw" \
  "${HOME}/.openclaw/workspace" \
  "${HOME}/.config/openclaw" \
  "${HOME}/.local/share" \
  "${HOME}/.homebrew"

case "${mode}" in
  gateway)
    exec /gateway-entrypoint.sh "$@"
    ;;
  shell|tmux)
    exec /launch-tmux.sh "$@"
    ;;
  raw)
    exec "$@"
    ;;
  *)
    # Unknown mode -> pass through to the openclaw CLI so `docker run ... onboard`
    # etc. still works for one-shot commands.
    exec node /app/dist/index.js "${mode}" "$@"
    ;;
esac
