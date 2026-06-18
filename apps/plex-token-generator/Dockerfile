FROM alpine:latest as cloner

ARG CHANNEL
ARG VERSION

RUN apk update && apk upgrade && \
    apk add --no-cache git

RUN git clone  https://github.com/Action3062/plex-token-generator.git /source


FROM nginxinc/nginx-unprivileged:alpine

COPY --from=cloner /source/. /usr/share/nginx/html/
