ARG VERSION
# --- builder: drone/envsubst (gleiche Semantik wie im alpine-Base) ---
FROM public.ecr.aws/docker/library/golang:1.20.4-alpine3.18 as builder
ARG TARGETOS
ARG TARGETARCH
ARG TARGETVARIANT=""
ARG TARGETPLATFORM
ENV GO111MODULE=on \
    CGO_ENABLED=0 \
    GOOS=${TARGETOS} \
    GOARCH=${TARGETARCH} \
    GOARM=${TARGETVARIANT}
RUN go install -ldflags="-s -w" github.com/drone/envsubst/cmd/envsubst@latest

#hadolint ignore=DL3018,DL3059
RUN \
    case "${TARGETPLATFORM}" in \
        'linux/amd64') \
            apk add --no-cache upx \
            && upx --ultra-brute /go/bin/envsubst \
        ;; \
    esac

# --- final: offizielles Ubuntu (Docker-Hub-Mirror auf ECR Public) ---
FROM public.ecr.aws/docker/library/ubuntu:${VERSION}
ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ENV TARGETPLATFORM=${TARGETPLATFORM:-linux/amd64}

ENV UMASK="0002" \
    TZ="Etc/UTC" \
    DEBIAN_FRONTEND="noninteractive"

WORKDIR /app

#hadolint ignore=DL3008
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates  bash         dnsutils \
        curl             iputils-ping jo \
        jq               moreutils    nano \
        pv               tini         tzdata \
        unzip            util-linux   wget \
        dumb-init \
    && (apt-get install -y --no-install-recommends unrar \
        || apt-get install -y --no-install-recommends unrar-free || true) \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#hadolint ignore=DL3059
RUN \
    groupadd -r appnest --gid 568 \
        && useradd -r -u 568 -g appnest -s /bin/bash appnest \
    && \
    mkdir -p /config \
    && chown -R appnest:appnest /config \
    && chmod -R 775 /config \
    && printf "/bin/bash /scripts/greeting.sh\n" > /etc/profile.d/greeting.sh \
    && printf "umask %d" "${UMASK}" > /etc/profile.d/umask.sh \
    && ln -sf /usr/bin/tini /sbin/tini \
    && ln -sf /usr/bin/nano /usr/local/bin/vi \
    && ln -sf /usr/bin/nano /usr/local/bin/vim \
    && ln -sf /usr/bin/nano /usr/local/bin/nano \
    && ln -sf /usr/bin/nano /usr/local/bin/neovim \
    && ln -sf /usr/bin/nano /usr/local/bin/emacs \
    && rm -rf /tmp/*

VOLUME ["/config"]
COPY ./apps/ubuntu/scripts /scripts
COPY --from=builder /go/bin/envsubst /usr/local/bin/envsubst
ENTRYPOINT ["/usr/bin/tini", "--"]
