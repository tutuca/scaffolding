#!/bin/bash

# VARIABLES -------------------------------------------------------------------
source "$HOME/variables.sh"
# -----------------------------------------------------------------------------

cd "$HOME"
curl -L --header "PRIVATE-TOKEN: $USER_TOKEN" "https://gitlab.com/api/v4/projects/26424709/jobs/artifacts/master/download?job=build" -o "$HOME/artifacts.zip"
unzip "$HOME/artifacts.zip" -d "$HOME/web"
rm "$HOME/artifacts.zip"
cd "$HOME/web"
make update
