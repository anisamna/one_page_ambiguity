FROM nginx:alpine as final

COPY nginx.conf /etc/nginx/conf.d/nginx.conf
RUN rm -rf /etc/nginx/conf.d/default.conf