FROM ghcr.io/action3062/alpine:rolling AS fetch

ARG VERSION
ARG CHANNEL=main

# Base already ships curl, tar, file - no extra apk needed.
# stable -> master, dev -> nightly (matches apps/radarr/ci/latest.sh).
# /updatefile redirects to the latest tarball for the branch; Servarr ignores
# ?version=, so we don't pin it in the URL.
RUN set -eux; \
    case "${CHANNEL}" in \
      dev) BRANCH=nightly ;; \
      *)   BRANCH=master ;; \
    esac; \
    URL="https://radarr.servarr.com/v1/update/${BRANCH}/updatefile?os=linuxmusl&runtime=netcore&arch=x64"; \
    echo "Fetching: ${URL}"; \
    curl -fL --retry 3 --retry-delay 2 --show-error \
      -A "github.com/action3062/containers" \
      -w 'curl: http=%{http_code} size=%{size_download} url=%{url_effective}\n' \
      -o /tmp/radarr.tar.gz "${URL}"; \
    ls -la /tmp/radarr.tar.gz; \
    mkdir -p /app/extract; \
    if ! tar xzf /tmp/radarr.tar.gz -C /app/extract; then \
      echo "tar failed; first 500 bytes of payload:"; \
      head -c 500 /tmp/radarr.tar.gz; echo; \
      exit 1; \
    fi; \
    echo "Extracted layout:"; ls -la /app/extract; \
    APP_DIR="$(find /app/extract -mindepth 1 -maxdepth 1 -type d | head -1)"; \
    test -n "${APP_DIR}" -a -d "${APP_DIR}"; \
    echo "App dir: ${APP_DIR}"; \
    mv "${APP_DIR}" /app/Radarr; \
    rm /tmp/radarr.tar.gz; \
    rm -rf /app/Radarr/package_info /app/Radarr/Radarr.Update; \
    ls -la /app/Radarr | head -10


FROM ghcr.io/action3062/alpine:rolling

ARG VERSION

LABEL org.opencontainers.image.title="radarr" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/radarr" \
      org.opencontainers.image.source="https://github.com/Radarr/Radarr"

# .NET on musl needs icu-libs + libstdc++/libgcc + sqlite-libs.
# Base image already ships ca-certificates, tini, tzdata, wget, curl, bash.
RUN apk add --no-cache \
      icu-data-full \
      icu-libs \
      libgcc \
      libstdc++ \
      sqlite-libs

COPY --from=fetch --chown=appnest:appnest /app/Radarr /app/radarr

USER appnest
WORKDIR /config

ENV XDG_CONFIG_HOME=/config \
    XDG_DATA_HOME=/config \
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=0 \
    COMPlus_EnableDiagnostics=0

EXPOSE 7878

HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD wget -qO- http://127.0.0.1:7878/ping >/dev/null 2>&1 || exit 1

# Base provides ENTRYPOINT ["/sbin/tini", "--"]; override CMD only.
CMD ["/app/radarr/Radarr", "--nobrowser", "--data=/config"]
