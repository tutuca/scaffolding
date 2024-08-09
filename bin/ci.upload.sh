#!/bin/sh

apk add -U make docker-compose

cp docker-compose.override-template.yml docker-compose.override.yml
cp nginx/nginx-template.conf nginx/nginx.conf
cp env-template .env

mkdir -p static artifacts

chown -R "${UID}:${GID}" static artifacts
adduser -u "${UID}" -g "$GID" -D app -h /home/app

docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" registry.gitlab.com

su app -m -c make upload
su app -m -c make bundle
