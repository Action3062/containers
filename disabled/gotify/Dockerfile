ARG VERSION
FROM gotify/server:${VERSION} as upstream
FROM ghcr.io/action3062/ubuntu:rolling 
COPY --from=upstream /app /app
WORKDIR /app
EXPOSE 80
USER 568
ENTRYPOINT ["./gotify-app"]