# =========================
# Source
# =========================
FROM alpine:latest AS cloner

ARG VERSION

RUN apk add --no-cache git

# uptime-kuma tags are not prefixed with "v" (e.g. 2.4.0)
RUN git clone --depth 1 -b "${VERSION}" https://github.com/louislam/uptime-kuma.git /source \
    && rm -rf /source/.git

# =========================
# Builder
# =========================
FROM node:20-alpine AS builder

WORKDIR /app

# Build deps for native modules (@louislam/sqlite3) on musl
#hadolint ignore=DL3018
RUN apk add --no-cache python3 make g++ py3-setuptools linux-headers

# Avoid pulling Chromium for transitive puppeteer deps
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1

COPY --from=cloner /source/. .

# Install (incl. dev deps for the Vite build), build the frontend, then drop dev deps
RUN npm ci \
    && npm run build \
    && npm prune --omit=dev \
    && mkdir -p /app/data

# =========================
# Runtime
# =========================
FROM node:20-alpine AS runner

ARG VERSION

LABEL org.opencontainers.image.title="uptime-kuma" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/uptime-kuma" \
      org.opencontainers.image.source="https://github.com/louislam/uptime-kuma"

WORKDIR /app

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3001 \
    UPTIME_KUMA_IS_CONTAINER=1

# iputils provides ping for monitor checks; dumb-init for signal handling/reaping
#hadolint ignore=DL3018
RUN apk add --no-cache iputils dumb-init

COPY --from=builder /app /app

VOLUME ["/app/data"]

EXPOSE 3001

HEALTHCHECK --interval=60s --timeout=30s --start-period=180s --retries=5 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:3001 || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server/server.js"]
