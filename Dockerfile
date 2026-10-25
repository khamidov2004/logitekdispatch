# Ultra-lightweight High-Performance Production Nginx Container
FROM nginx:alpine

# Remove default static content
RUN rm -rf /usr/share/nginx/html/*

# Copy web files
COPY index.html /usr/share/nginx/html/index.html
COPY favicon.png /usr/share/nginx/html/favicon.png
COPY logo.png /usr/share/nginx/html/logo.png

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
