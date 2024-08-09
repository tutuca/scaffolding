ENV ?= development
app := app
dump ?=
args ?=
compose = docker compose
run = $(compose) run --rm $(app)
manage = scaffolding
npm = $(run) npm
pip = uv pip
# pip = pip

VERSION = 0.1.8
IMG_NAME = registry.gitlab.com/bigpear.adm/scaffolding


# Compose related commands
start:
	$(compose) up $(args)

stop:
	$(compose) stop

configure:
	mkdir -p static media data data/backups
	cp etc/.env.skel .env
	cp etc/compose.override.yml.skel compose.override.yml
	cp etc/nginx/nginx.conf.skel etc/nginx/nginx.conf

logs:
	$(compose) logs -f $(app)

build:
	$(compose) build $(args)

build_docker:
	$(compose) build $(args)

build_wheel:
	python -m build

build: build_wheel build_docker

docs:
	python -m mkdocs build

install_backend:
	$(pip) install -e .[dev]

install_frontend:
	nodeenv -pn lts
	npm install

install: install_backend install_frontend

tag:
	docker tag "$(IMG_NAME)" "$(IMG_NAME):$(VERSION)"

bundle:
	$(npm) --prefix=/root/src run build
	$(manage) collectstatic --noinput

upload_docker:
	docker push "$(IMG_NAME)"
	docker push "$(IMG_NAME):$(VERSION)"

upload_wheel:
	TWINE_PASSWORD=${CI_REGISTRY_PASSWORD} TWINE_USERNAME=${CI_REGISTRY_USER} python -m twine upload --repository-url https://gitlab.com/api/v4/projects/${CI_PROJECT_ID}/packages/pypi dist/*

upload: bundle upload_docker upload_wheel


clean:
	$(run) rm -rf dist/* static/*
	$(compose) down
	$(compose) rm --force -v
	rm -rf artifacts

# Container shell
shell:
	$(run) /bin/bash

dbshell:
	$(run:app=db) /bin/bash

restart :
	$(compose) restart $(app)

migrations:
	$(manage) makemigrations

migrate:
	$(manage) migrate

reset_db:
	$(manage) reset_db --noinput -c

reset: reset_db migrate
	$(manage) createsuperuser


update: backup
	$(compose) stop
	$(compose) pull
	$(compose) up -d
	$(manage) migrate --no-input

backup:
	$(run:app=db) /root/bin/backup.sh

lint:
	ruff check src tests
	flake8 src tests
	mypy src tests --explicit-package-bases

restore:
	$(compose) stop app
	$(run:app=db) /root/bin/restore.sh $(dump)
	$(compose) restart app

list_backups:
	$(run:app=db) /root/bin/list_backups.sh

bootstrap: migrate
	$(manage) createsuperuser
	$(manage) collectstatic --noinput

.PHONY: start stop build docs configure install upload clean shell migrations migrate restore backup shell_plus bootstrap
