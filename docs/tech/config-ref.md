# Configuración

El proyecto sigue las recomendaciones de [12Factor](https://12factor.net/config) en cuanto al manejo de configuraciones.

## **Referencia de Variables de Entorno**

`DEBUG` default _`True`_

`ALLOWED_HOSTS` default _`*`_

`DB_NAME` default _`tren_db`_

`DB_USER` default _`scaffolding`_

`DB_PASS` default _`changeme`_

`DB_HOST` default _`db`_

`DB_PORT` default _`5432`_

`SENTRY_DSN` default _`https://public@sentry/1`_  # notar que `https://public@sentry` no es una real.


## **Archivos de configuración**

### **`.env`**

> no versionar

Ejemplo:

```bash
DEBUG=1
ALLOWED_HOSTS=*
DB_NAME=tren_db
DB_USER=scaffolding
DB_PASS=changeme
DB_HOST=db
DB_PORT=5432
SENTRY_DSN=https://public@sentry/1
```


Ejemplo con variables de seguridad:

```bash
# General
DEBUG=0

# Server Settings
ALLOWED_HOSTS=127.0.0.1,bigpear.com.ar,localhost,backend

# Server Security
CSRF_COOKIE_SECURE=1
SESSION_COOKIE_SECURE=1
SECURE_HSTS_SECONDS=63072000
SECURE_HSTS_INCLUDE_SUBDOMAINS=1
SECURE_HSTS_PRELOAD=1
SECURE_SSL_REDIRECT=1

# Database
DB_NAME=tren_db
DB_USER=scaffolding
DB_PASS=changeme
DB_HOST=db
DB_PORT=5432

# Email configuration
EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
EMAIL_HOST=<email_host>
EMAIL_PORT=<email_port>
SERVER_EMAIL=<admin_email_address>
DEFAULT_FROM_EMAIL=<info_email_address>
EMAIL_SUBJECT_PREFIX=<email_tag_frefix>

# Extra services
SENTRY_DSN=https://public@sentry/1
```


### **`docker-compose.yml`**

Configuraciones generales de servicios.

Referencia: https://docs.docker.com/compose/compose-file/


### **`docker-compose.override.yml`**

> no versionar

Ejemplo de docker-compose.override.yml para producción.

```yml
version: "3.4"

services:
    backend:
        restart: always
        depends_on:
            - db
        networks:
            - scaffolding
    frontend:
        command: echo disabled
        restart: "no"
        networks:
            - scaffolding
    nginx:
        restart: always
        volumes:
            - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
            - ./nginx/html:/usr/share/nginx/html:ro
            - ./static:/usr/share/nginx/static
            - ./media:/usr/share/nginx/media
        networks:
            - scaffolding
        depends_on:
            - backend
    db:
        restart: always
        volumes:
            - postgres:/var/lib/postgresql/data
        networks:
            - scaffolding
    scheduler:
        image: mcuadros/ofelia:latest
        restart: always
        command: daemon
        volumes:
            - /var/run/docker.sock:/var/run/docker.sock
            - ./scheduler/config.ini:/etc/ofelia.conf
        depends_on:
            - backend

networks:
    scaffolding:

volumes:
    postgres:
    backup:
```


### **`scheduler/scheduler.ini`**

```ini
[job-exec "Publish Scheduled Pages"]
schedule = @every 1m
container = web_backend_1
command = python manage.py publish_scheduled_pages -v3
```


### **`nginx.conf`**

Configuración de nginx con parámetros de seguridad para producción.

```conf
upstream backend {
    server                      backend:8000 fail_timeout=120;
}

server {
    server_name                 <sever_name>;
    keepalive_timeout           300;
    listen                      80;
    listen                      [::]:80;
    listen                      127.0.0.1:80;
    server_tokens               off;
    # Redirect server error pages to the static page /50x.html
    error_page                  500 502 503 504  /50x.html;
    # Redirect all requests to all URI from http to https
    add_header                  Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    add_header                  X-Content-Type-Options nosniff;
    add_header                  X-XSS-Protection "1; mode=block";
    return                      301 https://$server_name;
}


server {
    server_name                 <sever_name>;
    keepalive_timeout           300;
    listen                      443 ssl http2;
    listen                      [::]:443 ssl http2;
    # Redirect server error pages to the static page /50x.html
    error_page                  500 502 503 504 /50x.html;

    # Certificates
    ssl_certificate             <cert_file>;
    ssl_certificate_key         <key_file>;

    # SSL parameters
    ssl_protocols               TLSv1.2;
    ssl_ciphers                 ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256;
    ssl_prefer_server_ciphers   on;

    # Header configs
    add_header                  Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    add_header                  X-Content-Type-Options nosniff;
    add_header                  X-XSS-Protection "1; mode=block";

    types_hash_max_size         4069;
    client_max_body_size        4G;
    server_tokens               off;

    location = /50x.html {
        root        /usr/share/nginx/html;
    }

    location /media/ {
        root        /usr/share/nginx/;
        expires     30d;
    }

    location /static/ {
        root        /usr/share/nginx/;
        expires     30d;
    }

    location / {
        try_files   $uri @app;
    }

    location @app {
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        Host $http_host;
        proxy_redirect          off;
        proxy_pass              http://backend;
        break;
    }

}
```


### **`settings.py`**

Configuraciones de Django o Wagtail.

Django: https://docs.djangoproject.com/es/3.2/ref/settings/

Wagtail: https://docs.wagtail.io/en/stable/reference/contrib/settings.html

### **`package.json`**

Dependencias de frontend y metadatos del paquete Javascript.

Referencia: https://docs.npmjs.com/cli/v7/configuring-npm/package-json/


### **`webpack.config.js`**

Instrucciones de compilación para el frontend.

Referencia: https://webpack.js.org/configuration/


### **`pyproject.toml`**

Configuraciones del entorno del proyecto, lintters, formateadores, dependencias, herramientas de desarrollo, de documentación, entre otras.


### **`pre-commit-config.yaml`**

Configuraciónes para 'Hooks' de Git.

Referencia: https://pre-commit.com/hooks.html
