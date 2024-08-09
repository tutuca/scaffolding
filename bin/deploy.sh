#!/bin/bash

# VARIABLES -------------------------------------------------------------------
source "$HOME/variables.sh"
# -----------------------------------------------------------------------------

echo "Ejecutar como usuario $DEPLOY_USER"

cd "$HOME"
curl -L --header "PRIVATE-TOKEN: $USER_TOKEN" "https://gitlab.com/api/v4/projects/26424709/jobs/artifacts/master/download?job=build" -o "$HOME/artifacts.zip"
unzip "$HOME/artifacts.zip" -d "$HOME/web"
rm "$HOME/artifacts.zip"
docker login -u "$REGISTRY_USER" -p "$REGISTRY_PWD" registry.gitlab.com
cd "$HOME/web" && make configure
cp "$HOME/web/scheduler/config-template.ini" "$HOME/web/scheduler/config.ini"
editor "$HOME/web/.env" && editor "$HOME/web/docker-compose.override.yml" && editor "$HOME/web/scheduler/config.ini"

echo ""
echo "Ejecutar 'make install' para instalar, 'make bootstrap' para completar el registro y luego 'make start args=-d' para iniciar el sitio."
