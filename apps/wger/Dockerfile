ARG VERSION
FROM wger/server:${VERSION}
USER root

# Set default PUID and PGID
ENV PUID=568
ENV PGID=568

# Create default user and group
RUN groupadd -g ${PGID} appnest && \
    userdel wger && \
    useradd -u ${PUID} -g appnest -d /home/wger -s /bin/bash appnest && \
    chown appnest:appnest /home/wger -R

# Prepare for symlinks for static assets
RUN mkdir -p /config/static && \
    mkdir /config/media && \
    rm -rf /home/wger/static && \
    rm -rf /home/wger/media && \
    ln -s /config/static /home/wger/static && \
    ln -s /config/media /home/wger/media && \
    chown appnest:appnest /config -R

USER appnest
