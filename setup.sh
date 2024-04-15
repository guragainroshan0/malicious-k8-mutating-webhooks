#!/bin/bash

apt update -y

apt install -y certbot nginx python3-venv

# create venv and activate
python3 -m venv env
source env/bin/activate

# install python dependencies
pip3 install flask jsonify

# stop nginx as certbot might need it
systemctl stop nginx

# generate certificate
certbot certonly -d $DOMAIN --non-interactive --agree-tos -m mail@$DOMAIN --standalone

echo 'server {
         listen 443 ssl default_server;
         listen [::]:443 ssl default_server;
        ssl_certificate /etc/ssl/certs/localhost.crt;
        ssl_certificate_key /etc/ssl/private/localhost.key;
        location / {
                proxy_pass http://localhost:8080;
                }
        root /var/www/html;
        index index.html index.htm index.nginx-debian.html;
        server_name _;
}' > /etc/nginx/sites-enabled/default

# copy certificate to the required path
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/ssl/certs/localhost.crt
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/ssl/private/localhost.key

# start nginx
systemctl start nginx

# create flask service file
echo '[Unit]
Description=flask web server
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/malicious-k8-mutating-webhooks
Environment="PATH=/home/ubuntu/malicious-k8-mutating-webhooks/env/bin"
ExecStart=/home/ubuntu/malicious-k8-mutating-webhooks/env/bin/flask --app app.py --debug run --port 8080' > /etc/systemd/system/flask.service

# start flask service
systemctl start flask

