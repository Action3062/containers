ARG VERSION
FROM node:24-bookworm-slim

ARG VERSION

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      git \
      openssl \
      procps \
      python3 \
      tini && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# OpenClaw is published to npm; the GitHub release tag may be prefixed with "v".
RUN NPM_VERSION="${VERSION#v}" && \
    npm install -g --omit=dev "openclaw@${NPM_VERSION}" && \
    npm cache clean --force

RUN mkdir /config && chown node:node /config

USER node
WORKDIR /config

ENV NODE_ENV=production \
    HOME=/config \
    XDG_CONFIG_HOME=/config

EXPOSE 18789

ENTRYPOINT ["tini", "-s", "--"]
# Gateway binds to loopback by default; override to "lan" so the port is
# reachable across Docker's bridge network.
CMD ["openclaw", "gateway", "--bind", "lan"]

LABEL org.opencontainers.image.source="https://github.com/openclaw/openclaw"
