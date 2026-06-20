#!/usr/bin/env bash
# Starts the OpenClaw gateway, and optionally a ttyd web shell alongside it.
#
# Required when binding to LAN (0.0.0.0): auth credentials. We refuse to start
# with --bind lan and no credentials so a misconfigured pod can never expose an
# anonymous gateway to other tenants on the cluster.

set -euo pipefail

port="${OPENCLAW_GATEWAY_PORT:-18789}"
bind="${OPENCLAW_GATEWAY_BIND:-lan}"

if [[ "${bind}" == "lan" || "${bind}" == "0.0.0.0" ]]; then
  if [[ -z "${OPENCLAW_GATEWAY_AUTH_USER:-}" || -z "${OPENCLAW_GATEWAY_AUTH_PASSWORD:-}" ]]; then
    echo "ERROR: bind=${bind} requires OPENCLAW_GATEWAY_AUTH_USER and OPENCLAW_GATEWAY_AUTH_PASSWORD." >&2
    echo "       Refusing to start an unauthenticated gateway on a non-loopback address." >&2
    exit 1
  fi
fi

# A fresh container has no openclaw config until the customer runs
# `openclaw setup` from the web shell. Bring the gateway up in unconfigured
# mode in that window so /healthz works and the operator's k8s probes pass.
# Operator can force a strict start by setting OPENCLAW_REQUIRE_CONFIG=1.
extra_args=()
config_marker="${XDG_CONFIG_HOME:-${HOME}/.config}/openclaw/config.json"
if [[ ! -f "${config_marker}" && "${OPENCLAW_REQUIRE_CONFIG:-0}" != "1" ]]; then
  echo "INFO: no config at ${config_marker}; starting with --allow-unconfigured." >&2
  extra_args+=(--allow-unconfigured)
fi

# Optional ttyd web-shell on a separate port. Killed when the gateway exits.
if [[ "${OPENCLAW_RUN_TTYD:-0}" == "1" ]]; then
  ttyd_port="${TTYD_PORT:-7681}"
  ttyd_args=(
    --port "${ttyd_port}"
    --interface 0.0.0.0
    --writable
  )
  if [[ -n "${TTYD_AUTH_USER:-}" && -n "${TTYD_AUTH_PASSWORD:-}" ]]; then
    ttyd_args+=(--credential "${TTYD_AUTH_USER}:${TTYD_AUTH_PASSWORD}")
  else
    echo "WARN: TTYD_AUTH_USER/TTYD_AUTH_PASSWORD not set; ttyd will run without auth." >&2
  fi
  echo "Starting ttyd on :${ttyd_port}..."
  ttyd "${ttyd_args[@]}" /launch-tmux.sh &
  ttyd_pid=$!
  trap 'kill "${ttyd_pid}" 2>/dev/null || true' EXIT
fi

echo "Starting OpenClaw gateway on :${port} (bind=${bind})..."
exec node /app/dist/index.js gateway \
  --port "${port}" \
  --bind "${bind}" \
  "${extra_args[@]}" \
  "$@"
