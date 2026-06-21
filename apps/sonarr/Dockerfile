FROM ghcr.io/action3062/alpine:rolling AS fetch

ARG VERSION
ARG CHANNEL=main

# Base already ships curl, tar, file - no extra apk needed.
# stable -> master, dev -> main (matches apps/sonarr/ci/latest.sh).
RUN set -eux; \
    case "${CHANNEL}" in \
      dev) BRANCH=main ;; \
      *)   BRANCH=master ;; \
    esac; \
    URL="https://services.sonarr.tv/v1/update/${BRANCH}/updatefile?os=linuxmusl&runtime=netcore&arch=x64"; \
    echo "Fetching: ${URL}"; \
    curl -fL --retry 3 --retry-delay 2 --show-error \
      -A "github.com/action3062/containers" \
      -o /tmp/sonarr.tar.gz "${URL}"; \
    ls -la /tmp/sonarr.tar.gz; \
    mkdir -p /app/extract; \
    tar xzf /tmp/sonarr.tar.gz -C /app/extract; \
    rm /tmp/sonarr.tar.gz; \
    rm -f /app/extract/Sonarr/package_info /app/extract/Sonarr/Sonarr.Update; \
    ls -la /app/extract/Sonarr | head -10


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

COPY --from=fetch --chown=appnest:appnest /app/extract/Sonarr /app/sonarr

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
