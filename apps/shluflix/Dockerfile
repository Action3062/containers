# Get the meinappnest code
FROM alpine:latest as cloner

ARG CHANNEL
ARG VERSION

RUN apk update && apk upgrade && \
    apk add --no-cache git

RUN git clone  https://bitbucket.org/shluflix-stremio/shluflix.git /source

FROM ghcr.io/action3062/alpine-node:20
WORKDIR /app
COPY --from=cloner /source .
COPY apps/shluflix/branding/landingTemplate.js .
COPY apps/shluflix/branding/addon.js .
RUN npm install
CMD ["npm", "start"]
