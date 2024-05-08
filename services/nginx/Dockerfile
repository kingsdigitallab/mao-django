FROM nginx:${NGINX_VERSION:-stable-alpine}

COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
COPY ./nginx/robots.txt /usr/share/nginx/robots.txt
