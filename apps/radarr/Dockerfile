FROM alpine:3.20 AS fetch

ARG VERSION
ARG CHANNEL=main

RUN apk add --no-cache curl tar

# stable -> master, dev -> develop (apps/radarr/ci/latest.sh updated to match).
RUN case "${CHANNEL}" in \
      dev) BRANCH=develop ;; \
      *)   BRANCH=master ;; \
    esac && \
    curl -fsSL \
      "https://radarr.servarr.com/v1/update/${BRANCH}/updatefile?version=${VERSION}&os=linuxmusl&runtime=netcore&arch=x64" \
      -o /tmp/radarr.tar.gz && \
    mkdir -p /app && \
    tar xzf /tmp/radarr.tar.gz -C /app && \
    rm /tmp/radarr.tar.gz && \
    rm -f /app/Radarr/package_info /app/Radarr/Radarr.Update


FROM alpine:3.20

ARG VERSION

LABEL org.opencontainers.image.title="radarr" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/radarr" \
      org.opencontainers.image.source="https://github.com/Radarr/Radarr"

RUN apk add --no-cache \
      ca-certificates \
      icu-data-full \
      icu-libs \
      libgcc \
      libstdc++ \
      sqlite-libs \
      tini \
      tzdata && \
    update-ca-certificates && \
    addgroup -g 568 radarr && \
    adduser -D -u 568 -G radarr -h /config -s /sbin/nologin radarr && \
    install -d -o radarr -g radarr -m 0755 /config

COPY --from=fetch --chown=radarr:radarr /app/Radarr /app/radarr

USER radarr
WORKDIR /config

ENV XDG_CONFIG_HOME=/config \
    XDG_DATA_HOME=/config \
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=0 \
    COMPlus_EnableDiagnostics=0

EXPOSE 7878

HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD wget -qO- http://127.0.0.1:7878/ping >/dev/null 2>&1 || exit 1

ENTRYPOINT ["tini", "-s", "--"]
CMD ["/app/radarr/Radarr", "--nobrowser", "--data=/config"]
