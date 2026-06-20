FROM alpine:latest AS cloner

ARG VERSION=v2026.6.8
ARG SOURCE_CACHE_BUSTER=local

RUN apk update && apk upgrade && \
    apk add --no-cache git ca-certificates

RUN git clone -b "${VERSION}" https://github.com/openclaw/openclaw.git /source


FROM node:22-bookworm

ARG VERSION=v2026.6.8
ARG CHANNEL=main
ARG SOURCE_CACHE_BUSTER=local
ARG TTYD_VERSION=1.7.7
ARG TTYD_SHA256=8a217c968aba172e0dbf3f34447218dc015bc4d5e59bf51db2f2cd12b7be4f55

LABEL org.opencontainers.image.title="openclaw (main)" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/openclaw" \
      org.opencontainers.image.documentation="https://github.com/action3062/containers/tree/main/apps/openclaw/README.md" \
      org.opencontainers.image.source="https://github.com/openclaw/openclaw"

ENV NODE_ENV=production \
    HOME=/config \
    XDG_CONFIG_HOME=/config \
    XDG_DATA_HOME=/config/.local/share \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    OPENCLAW_GATEWAY_PORT=18789 \
    OPENCLAW_GATEWAY_BIND=loopback \
    TTYD_PORT=7681 \
    OPENCLAW_RUN_TTYD=0 \
    BUN_INSTALL=/opt/bun \
    PATH="/opt/bun/bin:/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Runtime packages, locales, fish/tmux for the customer shell, tini as PID 1.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      tini \
      tmux \
      fish \
      build-essential \
      procps \
      file \
      git \
      curl \
      ca-certificates \
      jq \
      locales \
      unzip && \
    sed -i 's/^# *\(en_US.UTF-8 UTF-8\)/\1/' /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=en_US.UTF-8 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ElfHosted-style UID/GID 568 for the node user, prepare /app and /config.
RUN groupmod -g 568 node && \
    usermod -u 568 -g 568 -d /config node && \
    install -d -o node -g node -m 0755 /app /config /config/.openclaw /config/.openclaw/workspace /config/.config/openclaw /config/.local/share

# Bun (kept on PATH for tooling; installed system-wide so every user can read it).
RUN curl -fsSL https://bun.sh/install -o /tmp/bun-install.sh && \
    bash /tmp/bun-install.sh && \
    rm /tmp/bun-install.sh && \
    chmod -R a+rX "${BUN_INSTALL}"

# corepack so pnpm matches the lockfile's packageManager pin.
RUN corepack enable

# Anthropic Claude Code CLI for the customer shell.
RUN npm install -g @anthropic-ai/claude-code@latest && \
    npm cache clean --force

WORKDIR /app

# Dependency-relevant files first so pnpm install stays cached across source-only changes.
COPY --chown=node:node --from=cloner /source/package.json /source/pnpm-lock.yaml /source/pnpm-workspace.yaml /source/.npmrc ./
COPY --chown=node:node --from=cloner /source/ui/package.json ./ui/package.json
COPY --chown=node:node --from=cloner /source/patches ./patches
COPY --chown=node:node --from=cloner /source/scripts ./scripts

USER node
RUN pnpm install --frozen-lockfile

COPY --chown=node:node --from=cloner /source/. .

RUN OPENCLAW_A2UI_SKIP_MISSING=1 pnpm build && \
    pnpm ui:build && \
    CI=true pnpm prune --prod && \
    pnpm store prune || true

USER root

# Pinned ttyd binary for the web-shell.
ADD --chmod=755 --checksum=sha256:${TTYD_SHA256} \
    https://github.com/tsl0922/ttyd/releases/download/${TTYD_VERSION}/ttyd.x86_64 \
    /usr/local/bin/ttyd

# Linuxbrew mount point (customer-installable; image ships the symlink target).
RUN install -d -o node -g node /home/linuxbrew && \
    ln -s /config/.homebrew /home/linuxbrew/.linuxbrew && \
    chown -h node:node /home/linuxbrew/.linuxbrew

# fish completions (CLI exists at this point because pnpm build ran).
RUN install -d /etc/fish/conf.d /etc/fish/functions /etc/fish/completions && \
    su node -c 'node /app/dist/index.js completion --shell fish' > /etc/fish/completions/openclaw.fish

# ElfHosted wrappers from the build context (repo root).
COPY --chmod=755 apps/openclaw/entrypoint.sh         /entrypoint.sh
COPY --chmod=755 apps/openclaw/gateway-entrypoint.sh /gateway-entrypoint.sh
COPY --chmod=755 apps/openclaw/launch-tmux.sh        /launch-tmux.sh
COPY            apps/openclaw/restricted.tmux.conf    /restricted.tmux.conf
COPY            apps/openclaw/openclaw-env.fish       /etc/fish/conf.d/openclaw-env.fish
COPY            apps/openclaw/openclaw.fish           /etc/fish/functions/openclaw.fish
COPY            apps/openclaw/fish_greeting.fish      /etc/fish/functions/fish_greeting.fish

RUN chown -R node:node /app /config /home/node

USER node
WORKDIR /config

EXPOSE 18789 7681

HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:'+(process.env.OPENCLAW_GATEWAY_PORT||18789)+'/healthz').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

ENTRYPOINT ["tini", "-s", "--", "/entrypoint.sh"]
CMD ["gateway"]
