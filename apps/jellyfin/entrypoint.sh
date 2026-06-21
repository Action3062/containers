#!/usr/bin/env bash

#shellcheck disable=SC1091
test -f "/scripts/umask.sh" && source "/scripts/umask.sh"

# Supervised transcode killer: enforces the per-plan transcode limits. It runs
# in the background and is restarted if it ever exits. Jellyfin stays the main
# (foreground) process, so the container lifecycle follows Jellyfin.
if [[ "${TRANSCODE_KILLER_ENABLED:-true}" == "true" ]]; then
    (
        while true; do
            python3 -u /transcode-killer.py
            echo "[entrypoint] transcode-killer exited ($?), restarting in 5s" >&2
            sleep 5
        done
    ) &
fi

exec \
    /usr/bin/jellyfin \
        --ffmpeg="/usr/lib/jellyfin-ffmpeg/ffmpeg" \
        --webdir="/usr/share/jellyfin/web" \
        --datadir="/config" \
        --cachedir="/config/cache" \
        "$@"
