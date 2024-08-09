# Guía de desarrollo

## **Backend**

Crear un virtualenv utilizando alguna version de python 3, preferiblemente 3.6.

    $ virtualenv -ppython3.7 scaffolding
    $ source scaffolding/bin/activate

Instalar las dependencias de desarrollo:

    (scaffolding) $ cd backend
    (scaffolding) $ pip install -r requirements.txt

> Alternativamente se puede "instalar" el proyecto, esto habilita a invocar un comando equivalente a `manage.py` desde cualquier ruta: `(scaffolding) $ python setup.py develop`.

El proyecto tiene valores por defecto que priorizan la ejecución rápida. Se pueden alterar declarando variables de entorno o un archivo `.env`.

Para la primera ejecución hace falta cargar las estructuras de las tablas y crear algún usuario administrador y recolectar los archivos estáticos de aplicaciones de terceros.

    (scaffolding) $ python manage.py migrate
    (scaffolding) $ python manage.py createsuperuser
    (scaffolding) $ python manage.py collectstatic

Ahora puede iniciar el servidor de desarrollo:

    (scaffolding) $ python manage.py runserver 0.0.0.0:8000

### Estilo de código y herramientas

- pep8: https://www.python.org/dev/peps/pep-0008/


## **Frontend**

Se recomienda instalar Node.js utilizando [nodeenv](http://ekalinin.github.io/nodeenv/).

    (scaffolding) $ pip install nodeenv
    (scaffolding) $ nodeenv -pn latest

Para utilizar el servidor web y el servicio de backend hace falta vincular la carpeta `static` en la raiz del repositorio. A la carpeta `frontend/dist`, configurada como objetivo de compilacion.

    $ ln -s static frontend/dist

Instalar las dependencias y ejecutar el compilador:

    (scaffolding) $ cd frontend
    (scaffolding) $ npm install
    (scaffolding) $ npm start

### Estilo de codigo y herramientas

Javascript:

- ES6: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference
- reglas de standard JS: https://standardjs.com/rules.html
- Sass: https://github.com/airbnb/css


## **Docker**

Se agregaron varios comandos de conveniencia alrededor de docker-compose.
Por ejemplo:

    $ make build

Construye todas las imágenes y servicios necesarios.

    $ make

Invoca el servidor de desarrollo.

    $ make shell

Abre una terminal en el contendor por defecto (`backend`), si necesita cambiar el servicio puede usar el flag `APP`:

    $ make shell APP=frontend


## **Datos de prueba**

Para los fines de validar funcionamientos y diseños mantenemos un conjunto de datos que ejercitan la mayor cantidad de casos posible.

## **Gestion de configuraciones**

- [Referencia de configuracion del proyecto](config-ref.md)
- [12factor](https://12factor.net/config)
- [django-environ](https://github.com/joke2k/django-environ)

Revisar:
- https://github.com/mrsteele/dotenv-webpack
