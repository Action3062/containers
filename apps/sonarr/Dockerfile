FROM ghcr.io/action3062/alpine:rolling AS fetch

ARG VERSION
ARG CHANNEL=main

# stable -> main (Sonarr v4 stable), dev -> develop.
#
# Sonarr's /v1/download/{branch} returns a JSON release manifest with all
# platform URLs, not a 302 to the tarball (regardless of os/arch/runtime
# query params). Fetch the JSON, parse the linuxMusl.x64 archive URL with
# jq (available in the base image), then download the actual tarball.
RUN set -eux; \
    case "${CHANNEL}" in \
      dev) BRANCH=develop ;; \
      *)   BRANCH=main ;; \
    esac; \
    META_URL="https://services.sonarr.tv/v1/download/${BRANCH}?version=${VERSION}"; \
    echo "Fetching metadata: ${META_URL}"; \
    curl -fL --retry 3 --retry-delay 2 --show-error \
      -A "github.com/action3062/containers" \
      -o /tmp/sonarr.json "${META_URL}"; \
    URL="$(jq -r '.linuxMusl.x64.archive.url' /tmp/sonarr.json)"; \
    if [ -z "${URL}" ] || [ "${URL}" = "null" ]; then \
      echo "Could not find .linuxMusl.x64.archive.url in metadata; full JSON:"; \
      cat /tmp/sonarr.json; echo; \
      exit 1; \
    fi; \
    echo "Tarball URL: ${URL}"; \
    curl -fL --retry 3 --retry-delay 2 --show-error \
      -A "github.com/action3062/containers" \
      -w 'curl: http=%{http_code} size=%{size_download} url=%{url_effective}\n' \
      -o /tmp/sonarr.tar.gz "${URL}"; \
    ls -la /tmp/sonarr.tar.gz; \
    mkdir -p /app/extract; \
    if ! tar xzf /tmp/sonarr.tar.gz -C /app/extract; then \
      echo "tar failed; first 500 bytes of payload:"; \
      head -c 500 /tmp/sonarr.tar.gz; echo; \
      exit 1; \
    fi; \
    echo "Extracted layout:"; ls -la /app/extract; \
    APP_DIR="$(find /app/extract -mindepth 1 -maxdepth 1 -type d | head -1)"; \
    test -n "${APP_DIR}" -a -d "${APP_DIR}"; \
    echo "App dir: ${APP_DIR}"; \
    mv "${APP_DIR}" /app/Sonarr; \
    rm /tmp/sonarr.tar.gz /tmp/sonarr.json; \
    rm -rf /app/Sonarr/package_info /app/Sonarr/Sonarr.Update; \
    ls -la /app/Sonarr | head -10


FROM ghcr.io/action3062/alpine:rolling

ARG VERSION

LABEL org.opencontainers.image.title="sonarr" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/sonarr" \
      org.opencontainers.image.source="https://github.com/Sonarr/Sonarr"

# .NET on musl needs icu-libs + libstdc++/libgcc + sqlite-libs.
# Base image already ships ca-certificates, tini, tzdata, wget, curl, bash.
RUN apk add --no-cache \
      icu-data-full \
      icu-libs \
      libgcc \
      libstdc++ \
      sqlite-libs

COPY --from=fetch --chown=appnest:appnest /app/Sonarr /app/sonarr

USER appnest
WORKDIR /config

ENV XDG_CONFIG_HOME=/config \
    XDG_DATA_HOME=/config \
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=0 \
    COMPlus_EnableDiagnostics=0

EXPOSE 8989

HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8989/ping >/dev/null 2>&1 || exit 1

# Base provides ENTRYPOINT ["/sbin/tini", "--"]; override CMD only.
CMD ["/app/sonarr/Sonarr", "--nobrowser", "--data=/config"]
