FROM alpine:3.20 AS fetch

ARG VERSION
ARG CHANNEL=main

RUN apk add --no-cache curl tar

# Matches apps/sonarr/ci/latest.sh: stable -> master branch, dev -> main branch.
RUN case "${CHANNEL}" in \
      dev) BRANCH=main ;; \
      *)   BRANCH=master ;; \
    esac && \
    curl -fsSL \
      "https://services.sonarr.tv/v1/update/${BRANCH}/updatefile?version=${VERSION}&os=linuxmusl&runtime=netcore&arch=x64" \
      -o /tmp/sonarr.tar.gz && \
    mkdir -p /app && \
    tar xzf /tmp/sonarr.tar.gz -C /app && \
    rm /tmp/sonarr.tar.gz && \
    rm -f /app/Sonarr/package_info /app/Sonarr/Sonarr.Update


FROM alpine:3.20

ARG VERSION

LABEL org.opencontainers.image.title="sonarr" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/sonarr" \
      org.opencontainers.image.source="https://github.com/Sonarr/Sonarr"

# .NET on musl needs icu-libs + libstdc++/libgcc, plus standard TLS / tz data.
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
    addgroup -g 568 sonarr && \
    adduser -D -u 568 -G sonarr -h /config -s /sbin/nologin sonarr && \
    install -d -o sonarr -g sonarr -m 0755 /config

COPY --from=fetch --chown=sonarr:sonarr /app/Sonarr /app/sonarr

USER sonarr
WORKDIR /config

ENV XDG_CONFIG_HOME=/config \
    XDG_DATA_HOME=/config \
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=0 \
    COMPlus_EnableDiagnostics=0

EXPOSE 8989

HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8989/ping >/dev/null 2>&1 || exit 1

ENTRYPOINT ["tini", "-s", "--"]
CMD ["/app/sonarr/Sonarr", "--nobrowser", "--data=/config"]
