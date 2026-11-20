FROM nginx:1.30.7-alpine@sha256:caf4e1e032a20f9c3c5e28fc7f25ffd768ad8677b4975c54193075997b3a97e3

RUN apk upgrade --update-cache --available && apk add openssl && rm -rf /var/cache/apk/*

RUN openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes -keyout /etc/nginx/self.key -out /etc/nginx/self.crt -subj "/CN=*"

COPY nginx.conf /etc/nginx/nginx.conf

#COPY version.txt /usr/share/nginx/html/version.txt

STOPSIGNAL SIGTERM

CMD ["nginx", "-g", "daemon off;"]

