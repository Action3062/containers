# =========================
# Source
# =========================
FROM alpine:latest AS cloner

ARG VERSION

RUN apk add --no-cache git

RUN git clone --depth 1 -b "v${VERSION}" https://github.com/gethomepage/homepage.git /source

# =========================
# Builder
# =========================
FROM node:22-alpine AS builder

WORKDIR /app

ARG VERSION

# Build deps for any native node-gyp modules on musl
#hadolint ignore=DL3018
RUN apk add --no-cache libc6-compat python3 make g++

COPY --from=cloner /source/. .

RUN mkdir -p config \
    && corepack enable \
    && pnpm install --frozen-lockfile --prefer-offline \
    && NEXT_TELEMETRY_DISABLED=1 \
       NEXT_PUBLIC_VERSION="v${VERSION}" \
       pnpm run build

# =========================
# Runtime
# =========================
FROM node:22-alpine AS runner

ARG VERSION

LABEL org.opencontainers.image.title="homepage" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/homepage" \
      org.opencontainers.image.source="https://github.com/gethomepage/homepage"

WORKDIR /app

ENV NODE_ENV=production \
    HOSTNAME=0.0.0.0 \
    PORT=3000

# Copy static assets and the Next.js standalone output
COPY --from=cloner /source/public ./public/
COPY --from=cloner --chmod=755 /source/docker-entrypoint.sh /usr/local/bin/
COPY --from=builder /app/.next/standalone/ ./
COPY --from=builder /app/.next/static/ ./.next/static

#hadolint ignore=DL3018
RUN apk add --no-cache su-exec iputils-ping shadow

VOLUME ["/config"]

EXPOSE ${PORT}

HEALTHCHECK --interval=10s --timeout=3s --start-period=20s \
  CMD wget --no-verbose --tries=1 --spider "http://127.0.0.1:${PORT}/api/healthcheck" || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["node", "server.js"]
