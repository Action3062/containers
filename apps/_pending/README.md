# Pending apps

Apps in this folder have a `metadata.json` and a `ci/latest.sh` upstream
version probe, but no `Dockerfile` yet — they are queued for image work.

## How this folder is treated by CI

- The `Image: Rebuild` workflow excludes `apps/_pending/**` from its
  push-path filter, so editing files inside this folder does **not**
  trigger a build matrix.
- `Release: Schedule` uses `find ./apps -mindepth 2 -maxdepth 2 -name
  metadata.json`, which only sees top-level `apps/<name>/`, so pending
  apps are not polled for upstream changes either.
- Renovate still sees the files but has nothing to bump until a
  Dockerfile is added.

## Promoting an app out of `_pending`

When you're ready to build one:

1. `git mv apps/_pending/<name> apps/<name>`
2. Add `Dockerfile` and `ci/goss.yaml`.
3. Local test: `task APP=<name> CHANNEL=main test`
4. Commit and push — the rebuild workflow will pick it up.
