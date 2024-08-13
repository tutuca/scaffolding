# scaffolding


## Organización del repositorio

```
.
├── README.md               -> Archivo de documentación para programadores.
├── LICENSE                 -> Noticia de licencia.
├── CHANGELOG               -> Registro de cambios.
├── Makefile                -> Utildades para el uso del componente.
├── compose.yml             -> Infraestructura como código usando docker-compose.
├── .gitlab-ci.yml          -> Instrucciones de construcción y despliegue.
├── pyproject.toml          -> Toolchain Python.
├── package.json            -> Toolchain Javascript.
├── docs/                   -> Documentación del componente.
├── bin/                    -> Utilidades auxiliares.
└── src/                    -> Código fuente del componente.
│   ├── Dockerfile          -> Utilidades auxiliares.
│   ├── common/             -> Clases base y utilidades genéricas.
│   ├── public/             -> Assets estáticos.
│   ├── samples/            -> Django App `Samples`.
│   ├── scaffolding/        -> Django project.
│   │   └── manage.py       -> Punto de entrada de la aplicación web.
│   ├── users/              -> Django App `Users`.
│   └── ui/                 -> Proyecto Vue para la interfaz gráfica.
│       ├── scss            -> Estilos usando Sass.
│       └── main.js         -> Punto de entrada para compilación.
├── VERSION                 -> Información de versión.
└── vite.config.js
```

## Instrucciones de instalación

Requisitos:

- Ubuntu 24.04+
- docker, docker-compose
- git
- make
- python 3.12+

Clonar el respositorio:

```
$ git clone git@gitlab.com:bigpear.adm/scaffolding.git
```

```
python -m venv .venv

source .venv/bin/activate

make configure
```

```
make install
```

## Uso


Para iniciar el servidor de backend, primero asegurarse de tener aplicadas todas las migraciones y crear un superusuario
```sh
$ scaffolding migrate

$ scaffolding createsuperuser
```

Luego podemos iniciar el servidor

```sh
$ scaffolding runserver
```

En otro terminal podemos compilar los assets de frontend:

Asegurarse de contar con una instalación de node, y descargar las dependencias:

```sh
$ nodeenv -pn lts
$ npm install
```

Ahora podemos iniciar el servidor de desarrollo:

```sh
$ npm start
```

## Documentación

- Documentos de mantenimiento
- Documentos de usuario

## Cómo contribuir
Ver `CONTRIBUTING`

> https://gitlab.com/bigpear.adm/scaffolding/-/wikis/home

## Noticia de licencia
Ver `LICENCE`
