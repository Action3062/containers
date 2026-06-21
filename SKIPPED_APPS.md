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

- **sabnzbd** — `ghcr.io/sabnzbd/sabnzbd:${VERSION}` returned "manifest not found".
  The upstream `sabnzbd-docker` Buildx publishes immutable tags like
  `4.5.2-4` (release suffix) rather than bare `4.5.2`. Either pull the
  tag with the trailing `-N` from a separate API call, or pin to the
  rolling `latest` tag and override at runtime via image digest.

## Source repository gone / no longer reachable

The git source referenced by `latest.sh` / `Dockerfile` is no longer
publicly available, so both the version resolve and the build fail.
Re-promote once a new source location is known (or wire in credentials
if it has merely gone private).

- **shluflix** — clones `https://bitbucket.org/shluflix-stremio/shluflix.git`.
  The Bitbucket git endpoint now returns 401 (auth required) and both the
  repo page and the whole `shluflix-stremio` workspace return 404, so the
  unauthenticated `git clone` / `git ls-remote` fail with
  "Authentication failed". The workspace 404 points to a deleted/renamed
  source rather than a simple private-flip. Find the new upstream (or add
  Bitbucket app-password creds) before re-promoting.
