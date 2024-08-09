#!/bin/bash

# IMPORTANTE ------------------------------------------------------------------
#
# Ejecutar como sudo.
#
# -----------------------------------------------------------------------------

# VARIABLES -------------------------------------------------------------------
source "$HOME/variables.sh"
# -----------------------------------------------------------------------------

DEPLOY_UID="1001"
DEPLOY_GID="1001"
apt -y	update
apt -y dist-upgrade
apt install -y docker-compose make unzip

echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
groupadd --gid $DEPLOY_GID deploy
echo "  "
echo "Introduzca una contraseña segura para el usuario de deploy"
echo "  "
adduser --uid $DEPLOY_UID --gid $DEPLOY_GID --gecos "Soporte,admin-web@scaffoldingsa.com.ar" $DEPLOY_USER
usermod -aG docker $DEPLOY_USER

curl -L --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64
chmod +x /usr/local/bin/gitlab-runner
useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash
gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner
gitlab-runner start
