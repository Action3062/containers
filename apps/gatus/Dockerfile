ARG VERSION
FROM twinproduction/gatus:v${VERSION} as upstream

FROM ghcr.io/action3062/alpine:rolling 

COPY --from=upstream /gatus /
COPY --from=upstream /config/config.yaml ./config/config.yaml

ENV PORT=8080
EXPOSE ${PORT}

ENTRYPOINT ["/gatus"]
