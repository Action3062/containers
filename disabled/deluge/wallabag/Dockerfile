ARG VERSION
FROM wallabag/wallabag:${VERSION} as upstream

# No need to run as root, nor to listen on port 80
RUN sed -i 's/listen 80/listen 8000/' /etc/nginx/nginx.conf

# Add appnest
RUN \
    addgroup -S appnest --gid 568 \
        && adduser -S appnest -G appnest --uid 568

# We use "appnest" as our user, not "nobody"
RUN chown -R appnest:appnest /var/www/wallabag && \
    sed -i 's/nobody/appnest/' /entrypoint.sh && \
    sed -i 's/nobody/appnest/' /etc/php81/php-fpm.conf

# half-baked attempt to avoid running as root
# COPY apps/wallabag/entrypoint.sh /
# USER 568