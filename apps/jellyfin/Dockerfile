FROM ghcr.io/action3062/ubuntu:jammy-20260509

ARG TARGETPLATFORM
ARG VERSION
ARG CHANNEL

# NVIDIA NVENC: the driver libraries are injected at runtime by the host's
# NVIDIA container runtime; these vars only advertise the capabilities.
ENV NVIDIA_DRIVER_CAPABILITIES="compute,video,utility" \
    NVIDIA_VISIBLE_DEVICES="all" \
    # Recommended by Jellyfin: disable glibc dynamic heap trimming
    MALLOC_TRIM_THRESHOLD_=131072

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# hadolint ignore=DL3008,DL3015,SC2086
RUN \
    apt-get -qq update \
    && apt-get -qq install -y --no-install-recommends \
        gnupg2 python3 libjemalloc2 \
    && \
    ARCH="$(dpkg --print-architecture)" \
    && \
    case "${TARGETPLATFORM:-linux/amd64}" in \
        'linux/amd64') \
            # Intel VAAPI / Quick Sync drivers (Ubuntu universe/multiverse, no external repo)
            EXTRA_INSTALL_ARG='intel-media-va-driver-non-free i965-va-driver mesa-va-drivers vainfo intel-opencl-icd ocl-icd-libopencl1'; \
        ;; \
        *) \
            EXTRA_INSTALL_ARG='mesa-va-drivers vainfo'; \
        ;; \
    esac \
    && \
    # Jellyfin official APT repository
    mkdir -p /etc/apt/keyrings \
    && curl -fsSL "https://repo.jellyfin.org/ubuntu/jellyfin_team.gpg.key" | gpg --dearmor -o /etc/apt/keyrings/jellyfin.gpg \
    && echo "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/jellyfin.gpg] https://repo.jellyfin.org/ubuntu jammy main" > /etc/apt/sources.list.d/jellyfin.list \
    && apt-get -qq update \
    && apt-get -qq install -y --no-install-recommends \
        ${EXTRA_INSTALL_ARG} \
        jellyfin-server="${VERSION}*" \
        jellyfin-web \
        jellyfin-ffmpeg7 \
    && \
    apt-get purge -y gnupg2 \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/*

# Replace malloc with jemalloc (better memory behaviour under transcoding load)
ENV LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libjemalloc.so.2"

# Per-plan transcode limits — override per customer/container.
# Unset *_TRANSCODES means unlimited; set JELLYFIN_API_KEY for graceful stops.
ENV JELLYFIN_ALLOW_4K="true" \
    JELLYFIN_URL="http://localhost:8096" \
    TRANSCODE_KILLER_ENABLED="true" \
    TRANSCODE_KILLER_INTERVAL="5"

LABEL org.opencontainers.image.title="jellyfin" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/jellyfin" \
      org.opencontainers.image.source="https://github.com/jellyfin/jellyfin"

COPY ./apps/jellyfin/entrypoint.sh /entrypoint.sh
COPY ./apps/jellyfin/transcode-killer.py /transcode-killer.py

# 8096 http · 8920 https · 7359/udp client discovery · 1900/udp DLNA
EXPOSE 8096 8920 7359/udp 1900/udp

VOLUME ["/config"]

USER 568

# Base image ENTRYPOINT is tini; entrypoint starts the killer + execs Jellyfin
CMD ["/entrypoint.sh"]
