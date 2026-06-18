FROM ghcr.io/action3062/alpine:rolling 

# Install dante-server, sockd user will be created
RUN apk add --no-cache curl tinyproxy
# Default configuration
COPY apps/tinyproxy/entrypoint.sh /

USER 568

ENTRYPOINT ["/entrypoint.sh"]

