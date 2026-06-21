FROM ghcr.io/action3062/alpine:rolling AS fetch

ARG VERSION
ARG CHANNEL=master

# CHANNEL is the branch name directly (master/develop/nightly); Lidarr's
# /updatefile redirects to the tarball when os+arch+runtime are passed.
RUN set -eux; \
    URL="https://lidarr.servarr.com/v1/update/${CHANNEL}/updatefile?os=linuxmusl&runtime=netcore&arch=x64"; \
    echo "Fetching: ${URL}"; \
    curl -fL --retry 3 --retry-delay 2 --show-error \
      -A "github.com/action3062/containers" \
      -w 'curl: http=%{http_code} size=%{size_download} url=%{url_effective}\n' \
      -o /tmp/lidarr.tar.gz "${URL}"; \
    ls -la /tmp/lidarr.tar.gz; \
    mkdir -p /app/extract; \
    if ! tar xzf /tmp/lidarr.tar.gz -C /app/extract; then \
      echo "tar failed; first 500 bytes:"; \
      head -c 500 /tmp/lidarr.tar.gz; echo; exit 1; \
    fi; \
    APP_DIR="$(find /app/extract -mindepth 1 -maxdepth 1 -type d | head -1)"; \
    test -n "${APP_DIR}" -a -d "${APP_DIR}"; \
    mv "${APP_DIR}" /app/Lidarr; \
    rm /tmp/lidarr.tar.gz; \
    rm -rf /app/Lidarr/package_info /app/Lidarr/Lidarr.Update; \
    ls -la /app/Lidarr | head -10


FROM ghcr.io/action3062/alpine:rolling

ARG VERSION

LABEL org.opencontainers.image.title="lidarr" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/lidarr" \
      org.opencontainers.image.source="https://github.com/Lidarr/Lidarr"

# .NET on musl + Servarr runtime deps. Lidarr also needs libchromaprint
# at runtime for audio fingerprinting (it ships fpcalc inside the tarball
# but expects the host lib for some codecs).
RUN apk add --no-cache \
      chromaprint \
      icu-data-full \
      icu-libs \
      libgcc \
      libstdc++ \
      sqlite-libs

COPY --from=fetch --chown=appnest:appnest /app/Lidarr /app/lidarr

USER appnest
WORKDIR /config

ENV XDG_CONFIG_HOME=/config \
    XDG_DATA_HOME=/config \
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=0 \
    COMPlus_EnableDiagnostics=0

EXPOSE 8686

HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8686/ping >/dev/null 2>&1 || exit 1

# Base provides ENTRYPOINT ["/sbin/tini", "--"]; override CMD only.
CMD ["/app/lidarr/Lidarr", "--nobrowser", "--data=/config"]
