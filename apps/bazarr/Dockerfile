FROM ghcr.io/action3062/alpine:rolling AS fetch

ARG VERSION

# Bazarr publishes source zips per release tag on GitHub; pull the archive
# tarball directly (always available, no auth) and normalize the extracted
# directory name to /app/bazarr.
RUN set -eux; \
    URL="https://github.com/morpheus65535/bazarr/archive/refs/tags/v${VERSION}.tar.gz"; \
    echo "Fetching: ${URL}"; \
    curl -fL --retry 3 --retry-delay 2 --show-error \
      -A "github.com/action3062/containers" \
      -w 'curl: http=%{http_code} size=%{size_download}\n' \
      -o /tmp/bazarr.tar.gz "${URL}"; \
    ls -la /tmp/bazarr.tar.gz; \
    mkdir -p /app/extract; \
    tar xzf /tmp/bazarr.tar.gz -C /app/extract; \
    rm /tmp/bazarr.tar.gz; \
    APP_DIR="$(find /app/extract -mindepth 1 -maxdepth 1 -type d | head -1)"; \
    test -n "${APP_DIR}" -a -d "${APP_DIR}"; \
    mv "${APP_DIR}" /app/bazarr; \
    test -f /app/bazarr/bazarr.py; \
    ls -la /app/bazarr | head -10


FROM ghcr.io/action3062/alpine:rolling

ARG VERSION

LABEL org.opencontainers.image.title="bazarr" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/bazarr" \
      org.opencontainers.image.source="https://github.com/morpheus65535/bazarr"

# Runtime deps: Python 3, ffmpeg/mediainfo for media probing, libxml2/libxslt
# for the lxml wheels. Pre-install lxml + numpy from apk (they have heavy
# native deps) so pip doesn't try to build them from source.
RUN apk add --no-cache \
      ffmpeg \
      libxml2 \
      libxslt \
      mediainfo \
      python3 \
      py3-lxml \
      py3-numpy \
      py3-pip \
      py3-setuptools \
      py3-wheel

COPY --from=fetch /app/bazarr /app/bazarr

# Build toolchain only while pip compiles native extensions, then dropped.
RUN apk add --no-cache --virtual .build-deps \
      cargo \
      g++ \
      gcc \
      libffi-dev \
      libxml2-dev \
      libxslt-dev \
      musl-dev \
      python3-dev \
      rust \
    && pip install --no-cache-dir --break-system-packages \
        --requirement /app/bazarr/requirements.txt \
    && apk del .build-deps \
    && rm -rf /root/.cache /root/.cargo /tmp/* \
    && find /usr/lib/python3* -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

RUN chown -R appnest:appnest /app/bazarr

USER appnest
WORKDIR /config

ENV PYTHONUNBUFFERED=1 \
    HOME=/config \
    XDG_CONFIG_HOME=/config

EXPOSE 6767

HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
  CMD wget -qO- http://127.0.0.1:6767/ >/dev/null 2>&1 || exit 1

# Base provides ENTRYPOINT ["/sbin/tini", "--"]; override CMD only.
CMD ["python3", "/app/bazarr/bazarr.py", "--no-update", "--config", "/config"]
