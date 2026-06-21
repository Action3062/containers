ARG VERSION
FROM ghcr.io/sabnzbd/sabnzbd:${VERSION}

ARG VERSION

LABEL org.opencontainers.image.title="sabnzbd" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/sabnzbd" \
      org.opencontainers.image.source="https://github.com/sabnzbd/sabnzbd"

# Upstream ships /config but as root-owned; make it writable for our
# appnest-style 568 user so the customer can fsGroup match it.
RUN mkdir -p /config && chmod 0775 /config

EXPOSE 8080
