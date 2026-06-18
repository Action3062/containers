ARG VERSION
FROM golift/notifiarr:${VERSION} as upstream

FROM ghcr.io/action3062/alpine:rolling 

# Create data folder and Install needed libraries
RUN apk add --no-cache \
        ca-certificates \
        curl \
        openssl \
        tzdata

# Make sure we have an ssl cert chain and timezone data.
COPY --from=upstream /notifiarr /notifiarr

ENV TZ=UTC

# Notifiarr specific.
# ENV PATH=$PATH:/
ENV USER=appnest

EXPOSE 5454
ENTRYPOINT [ "/notifiarr" ]