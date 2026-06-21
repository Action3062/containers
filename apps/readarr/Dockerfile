FROM ghcr.io/action3062/alpine:rolling AS fetch

ARG VERSION
ARG CHANNEL=develop

# CHANNEL maps straight to the branch name (develop/nightly).
RUN set -eux; \
    URL="https://readarr.servarr.com/v1/update/${CHANNEL}/updatefile?os=linuxmusl&runtime=netcore&arch=x64"; \
    echo "Fetching: ${URL}"; \
    curl -fL --retry 3 --retry-delay 2 --show-error \
      -A "github.com/action3062/containers" \
      -w 'curl: http=%{http_code} size=%{size_download} url=%{url_effective}\n' \
      -o /tmp/readarr.tar.gz "${URL}"; \
    ls -la /tmp/readarr.tar.gz; \
    mkdir -p /app/extract; \
    if ! tar xzf /tmp/readarr.tar.gz -C /app/extract; then \
      echo "tar failed; first 500 bytes:"; \
      head -c 500 /tmp/readarr.tar.gz; echo; exit 1; \
    fi; \
    APP_DIR="$(find /app/extract -mindepth 1 -maxdepth 1 -type d | head -1)"; \
    test -n "${APP_DIR}" -a -d "${APP_DIR}"; \
    mv "${APP_DIR}" /app/Readarr; \
    rm /tmp/readarr.tar.gz; \
    rm -rf /app/Readarr/package_info /app/Readarr/Readarr.Update; \
    ls -la /app/Readarr | head -10


FROM ghcr.io/action3062/alpine:rolling

ARG VERSION

LABEL org.opencontainers.image.title="readarr" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/readarr" \
      org.opencontainers.image.source="https://github.com/Readarr/Readarr"

RUN apk add --no-cache \
      icu-data-full \
      icu-libs \
      libgcc \
      libstdc++ \
      sqlite-libs

COPY --from=fetch --chown=appnest:appnest /app/Readarr /app/readarr

USER appnest
WORKDIR /config

ENV XDG_CONFIG_HOME=/config \
    XDG_DATA_HOME=/config \
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=0 \
    COMPlus_EnableDiagnostics=0

EXPOSE 8787

HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8787/ping >/dev/null 2>&1 || exit 1

CMD ["/app/readarr/Readarr", "--nobrowser", "--data=/config"]
