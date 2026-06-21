# Skipped apps

Apps in `apps/_pending/` whose Dockerfile work is paused, with the
reason. Each entry should be revisited if the blocker changes.

## Privater Action3062-Fork (build fork instead of upstream)

These reference `Action3062/<app>` in their `ci/latest.sh` or its
comments; the image is meant to be built from a private fork, not the
public upstream source. Outside the scope of this batch.

- catbox
- chillibridge
- debridge
- docs-internal
- ffprobe-shim
- forwardauthorizer
- itsout
- jackettio
- litterbox
- nest-bot
- nest-courier
- nest-gatekeeper
- nest-orchestrator
- nest-orchestrator-gitops
- nest-orchestrator-woo
- nest-worker
- nzbdav
- plex-debrid
- plexio
- prowlarr
- slate
- sootio
- zyclops

## Needs CI secret (ZURG_GH_CREDS / PLEX_TOKEN / etc.)

`latest.sh` authenticates against a private GitHub or vendor API to
resolve the version. Without the secret in the workflow env the build
arg is empty and `FROM upstream:` becomes invalid. Add the secret to
the workflow and re-promote.

- comet (needs `ZURG_GH_CREDS` for `g0ldyy/comet` API rate limits)

## Complex source-build (Playwright / Chromium / GPU)

These ship an Ubuntu-based upstream image and pull Chromium at build
time. Building on alpine would require a non-trivial Playwright port.

- byparr (FlareSolverr-style CF bypasser, Playwright + Chromium)

## Investigating upstream image tag format

Upstream image exists but the published tag format doesn't match what
`latest.sh` returns (e.g. `4.5.2` vs `v4.5.2` vs `release-4.5.2`).
Needs a per-app tag-mapping pass.

_(none confirmed yet — initial guesses for sabnzbd, freshrss, jellystat,
flatnotes, stremthru pending CI verdict.)_
