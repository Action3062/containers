ARG VERSION
FROM rednoah/filebot:node as upstream

RUN \
    adduser appnest \
        --uid 568 \
        --group \
        --system \
        --disabled-password \
        --home /data/node

ENV PUID=568 PGID=568

ENTRYPOINT ["/opt/filebot-node/start"]
USER 568
