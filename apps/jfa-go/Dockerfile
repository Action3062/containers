# Builds Action3062/jfa-go @ feature/paypal-stripe-integration from source.
#
# Mirrors the fork's own Dockerfile (goreleaser build inside the upstream build
# image, distroless runtime) but clones the branch instead of using the build
# context as the source tree (the build context here is the containers repo).
FROM --platform=$BUILDPLATFORM docker.io/hrfee/jfa-go-build-docker:latest AS support

ARG VERSION
ARG CHANNEL
ARG BUILT_BY=meinappnest
ENV JFA_GO_BUILT_BY=$BUILT_BY

# Full clone (not shallow): scripts/version.sh runs `git describe --tags`
RUN git clone -b feature/paypal-stripe-integration https://github.com/Action3062/jfa-go.git /opt/build

# Inject the BTCPay client package that is missing from the branch:
# api-btcpay.go imports github.com/hrfee/jfa-go/btcpay, but the btcpay/ package
# was never committed to the fork. Verified to make the branch compile.
COPY ./apps/jfa-go/btcpay/btcpay.go /opt/build/btcpay/btcpay.go

RUN cd /opt/build \
    && INTERNAL=off UPDATER=docker ./scripts/version.sh goreleaser build --snapshot --skip=validate --clean --id notray-e2ee
RUN mv /opt/build/dist/*_linux_arm_6 /opt/build/dist/placeholder_linux_arm
RUN sed -i 's#id="password_resets-watch_directory" placeholder="/config/jellyfin"#id="password_resets-watch_directory" value="/jf" disabled#g' /opt/build/build/data/html/setup.html

FROM gcr.io/distroless/base:latest AS final

ARG VERSION
ARG TARGETARCH

LABEL org.opencontainers.image.title="jfa-go" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="https://github.com/action3062/containers/tree/main/apps/jfa-go" \
      org.opencontainers.image.source="https://github.com/Action3062/jfa-go"

COPY --from=support /opt/build/dist/*_linux_${TARGETARCH}* /jfa-go
COPY --from=support /opt/build/build/data /jfa-go/data

EXPOSE 8056
EXPOSE 8057

VOLUME ["/data"]

CMD [ "/jfa-go/jfa-go", "-data", "/data" ]
