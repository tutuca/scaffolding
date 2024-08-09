# Instrucciones de instalación y mantenimiento.

##### Tabla de contenidos

- [Instrucciones de instalación y mantenimiento.](#instrucciones-de-instalación-y-mantenimiento)
        - [Tabla de contenidos](#tabla-de-contenidos)
  - [Requerimientos](#requerimientos)
  - [**Preparación del entorno**](#preparación-del-entorno)
    - [Instalar paquetes base](#instalar-paquetes-base)
    - [Crear usuario `deploy`](#crear-usuario-deploy)
    - [Instalación `gitlab-runner`](#instalación-gitlab-runner)
      - [Agregar usuario `gitlab-runner` a `docker` group](#agregar-usuario-gitlab-runner-a-docker-group)
      - [Registrar nuevo `runner` de `gitlab-runner`](#registrar-nuevo-runner-de-gitlab-runner)
    - [Despliegue inicial](#despliegue-inicial)
      - [Generar Personal Access Token - `PAT`](#generar-personal-access-token---pat)
      - [Descarga y extracción de `artifacts`](#descarga-y-extracción-de-artifacts)
        - [Descarga `artifacts`](#descarga-artifacts)
        - [Extracción `artifacts`](#extracción-artifacts)
      - [Generar `Deploy Token`](#generar-deploy-token)
        - [Autenticacion `docker`](#autenticacion-docker)
    - [Archivo `Makefile`](#archivo-makefile)
    - [Archivo pyproject](#archivo-pyproject)
    - [Archivo pre-commit-config](#archivo-pre-commit-config)
  - [**Actualización**](#actualización)
    - [Actualización manual](#actualización-manual)
    - [Despliegue continuo](#despliegue-continuo)
      - [Variables de entorno](#variables-de-entorno)
      - [Activación de despliegue](#activación-de-despliegue)
  - [**Actualización de certificados**](#actualización-de-certificados)

---

## Requerimientos

- Ubuntu Server `v23.10` o posterior.
- Docker `v24.0.5` o posterior.
- Al menos 1gb de RAM.
- Al menos 2 nucleos de CPU.

## **Preparación del entorno**

Estos pasos son necesarios de realizar por única vez al preparar un entorno de operaciones.

### Instalar paquetes base

```bash
sudo apt -y update && sudo apt -y dist-upgrade
sudo apt install -y docker-compose make unzip
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### Crear usuario `deploy`

Para evitar ataques por escalamiento de permisos, la aplicación se ejecuta en
modo usuario.

> Se utiliza `deploy` como nombre de usuario por convención.

```bash
sudo groupadd --gid 1001 deploy
sudo adduser --uid 1001 --gid 1001 --gecos "Soporte,admin-web@bigpear.com.ar" deploy
sudo usermod -aG docker deploy
```

### Instalación `gitlab-runner`

**Debido a que al momento de actualizar la documentación no existe un package `.deb` para `gitlab-runner`, es necesario realizar la descarga del mismo directamente con el siguiente comando.**

```bash
# NOTE: Realizar instalación con usuario *root*

  sudo curl -L --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64
  sudo chmod +x /usr/local/bin/gitlab-runner
  sudo useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash
  sudo gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner
  sudo gitlab-runner start
```

> Para verificar que la instalación haya sido exitosa, puede ejecutar `gitlab-runner -h`

#### Agregar usuario `gitlab-runner` a `docker` group

Para poder ejecutar comandos de Docker, es necesario agregar el usuario `gitlab-runner` al grupo de Docker. Ejecute el siguiente comando:

```bash
sudo usermod -aG docker gitlab-runner
```

Para mas información, consulte [usar el ejecutor de shell](https://docs.gitlab.com/ee/ci/docker/using_docker_build.html#use-the-shell-executor).

#### Registrar nuevo `runner` de `gitlab-runner`

Ejecute el siguiente comando, reemplazando segun corresponda:

```bash
sudo gitlab-runner register -n \
	--url='https://gitlab.com/' \
	--registration-token=<registration_token> \
	--name='Produccion' \
	--tag-list='production' \
	--executor='shell'
```

- `<registration_token>`
  En `Settings` del repositorio -> [`CI/CD`](https://gitlab.com/bigpear/scaffolding-a-las-nubes/-/settings/ci_cd) -> `Runners` podrá encontrarlo.

> Para mas información:
>
> - [Shell Executor](https://docs.gitlab.com/runner/executors/shell.html)

---

### Despliegue inicial

Al configurar el entorno por primera vez, es necesario realizar una serie de configuraciones.

Para ello: reinicie la máquina e inicie sesión como el usuario `deploy`.

#### Generar Personal Access Token - `PAT`

En la administración de su **cuenta usuario** en GitLab genere un
[Personal Access Token - `PAT`](https://gitlab.com/-/user_settings/personal_access_tokens) con nivel de acceso `api`.

Copie las credenciales y guardelas en un lugar segura.

#### Descarga y extracción de `artifacts`

##### Descarga `artifacts`

Muevase a la carpeta donde funcionará la instalación y descargue los archivos
necesarios utilizando el siguiente comando, reemplazando cada campo segun corresponda:

```bash
cd "$HOME"
curl -L --header "PRIVATE-TOKEN: <personal_access_token>" "https://gitlab.com/api/v4/projects/<project_id>/jobs/artifacts/<target_branch>/download?job=<job_target>" -o "$HOME/artifacts.zip"
```

- `<personal_access_token>`
  Token de acceso generado en paso anterior.
- `<project_id>`
  ID del proyecto.
- `<target_branch>`
  Rama desde la que se hara el deploy, eg: `main_branch`.
- `<job_target>`
  `job` de `CICD` **que genera** el `artifacts.zip`, eg: `build_wheel`.
  ***

##### Extracción `artifacts`

Extraiga el `artifacts` descargado:

```bash
# Extraer artifacts.
unzip "$HOME/artifacts.zip" -d "$HOME/web"
# Remover artifacts.
rm "$HOME/artifacts.zip"
```

#### Generar `Deploy Token`

Dirijase a la seccion `Settings` del repositorio, luego en la seccion `Repository`, finalmente seleccione la seccion `Deploy Tokens`.

Genere uno nuevo, deberá ingresar un nombre de usuario y la clave será generada de manera automática.

Los permisos necesarios son los siguientes:

- `read_repository`
- `write_registry`
- `write_package_registry`

> Es necesario que guarde de manera segura el `Password`, ya que podrá visualizarlo solo una vez.

##### Autenticacion `docker`

Registrese en `docker` con el usuario y la clave de `registry` generados en el paso anterior, para poder descargar las imágenes

Reemplace segun corresponda:

- `<user_registry>`
- `<password_registry>`

```bash
docker login -u <user_registry> -p <password_registry> registry.gitlab.com
```

### Archivo `Makefile`

En el directorio `/home/deploy/web` encontrará un archivo `Makefile`, el mismo contiene los comandos necesarios para completar el proceso.

Dirijase al directorio `/home/deploy/web` y ejecute el siguiente comando:

```bash
cd "$HOME/web"
make configure
```

Modifique los archivos `docker-compose.override.yaml` , `.env` y `nginx/nginx.conf` de acuerdo a las necesidades de producción. En el documento [referencia de configuraciones](config-ref.md#nginxconf) se proveen ejemplos de configuración de funcionamiento mínimas.

Finalmente ejecute `make bootstrap` completando con el usuario administrador y con una contraseña segura. Tome nota de esta información **en un lugar seguro**.

Luego ejecute `make start args='-d'` para iniciar el sitio web.

```bash
make install
cp "$HOME/web/scheduler/config-template.ini" "$HOME/web/scheduler/config.ini"
make bootstrap
make start args='-d'
```
### Archivo pyproject

Este archivo posee las configuraciones del entorno del proyecto, para instalar las dependencias del proyecto debe ejecutar lo siguiente:

``` sh
$ pip install -e .
```

En el caso de sólo querer instalar algunas de las herramientas, por ejemplo las de desarrollo, debe ejecutar:

``` sh
$ pip install -e .[dev]
```

Para actualizar las dependencias:

``` sh
$ pip install -U pyproject.toml
```

### Archivo pre-commit-config

Este archivo posee las configuraciones de Pre-Commit, herramienta que administra los hooks de git, actualmente con hooks de:
* Ruff
* Autoflake
* Flake8
* Prettier

Para utilizar la herramienta pre-commit debe activarla con:

``` sh
$ pre-commit install
```

> Dichos hooks correrán en la instancia de commits de Git, y hasta que no sean exitosos todos no permitirá continuar con los pasos de Git.

Para correr los hooks sin realizar un commit debe ejecutar:

``` sh
$ pre-commit run --all-files
```

En caso de querer desactivar la herramienta pre-commit debe ejecutar:

``` sh
$ pre-commit uninstall
```

## **Actualización**

Para actualizar una nueva versión.

### Actualización manual

La actualización manual similar es al despliegue inicial, omitiendo algunas configuraciones. Se deben ejecutar los siguientes pasos:

1. Iniciar sesión ssh en el servidor, preferiblemente con el usuario `deploy`.
2. En caso de que se haya conectado con el usuario `root`, cambiar de usuario con `sudo su deploy`.
3. Ir al home del usuario deploy con cd, `/home/deploy`.
4. Si existe en el directorio el archivo `artifacts.zip`:
   - Eliminarlo con el comando `rm artifacts.zip`.
   - Eliminar el directorio artifacts con el comando `rm -rf artifacts/`.
5. Ejecutar el comando en [Descarga `artifacts`](#descarga-artifacts), reemplazando cada campo segun corresponda.
6. Verificar que el archivo este en el directorio y que tenga contendido con el comando `ls -la`.
7. Extraer `artifacts.zip` en la carpeta `web`, ver [Extracción `artifacts`](#extracción-artifacts).
8. Acceder al directorio web con el comando `cd web`.
9. Ejecutar `make update`
10. Ejecutar `make compilemessages`. Esto introduce las traducciones de la parte programática en caso de que haya nuevas. Recomendamos hacerlo en cada despliegue.
11. Para verificar el cambio de version abir el archivo readme con el comando `less README.md`

### Despliegue continuo

Si configuró la integración contínua, puede realizar una actualización desde gitlab.

En el menú lateral, encontrará la seccion `Build`. Realice click sobre la misma y podrá visualizar una seccion llamada `Pipelines`, realice click nuevamente sobre esta.

Aqui podrá encontrar el historial completo de las ultimas ejecuciones del sistema de integración continua.

#### Variables de entorno

Deberá agregara dos variables de entorno, las mismas seran utilizas por el despliegue continuo de Gitlab y son creadas/modificadas en la seccion `Settings` -> `CI/CD` -> `Variables`:

- `ALPHA_RUNNER_ID`

  Una vez que usted haya [registrado nuevo `runner`](#registrar-nuevo-runner-de-gitlab-runner) obtenga el ID **alfanumérico** del mismo.
  Se utiliza para obtener el ultimo build generado por `gitlab-runner` y copiar archivos necesarios de manera automatica. Por esta razon, es necesario que verifique la carpeta generada y coloque el valor de la misma.

  > Para mas informacion ver archivo `gitlab-ci.yml`, job `deploy_production`.

#### Activación de despliegue

Puede ejecutar un despliegue eligiendo el entorno de destino y accionando `play` desde el desplegable de acciones de cada `job`.

![actions](../imgs/pipelines.png)

## **Actualización de certificados**

Para renovar los certificados SSL es necesario copiar el par `bigpear.pem` `bigpear.keys` a la carpeta `/home/deploy/certs` del servidor.

```bash
scp /mis-certificados/bigpear.* deploy@environment:/home/deploy/certs
```

> Reemplace `environment` con el nombre del entorno en su red, ej: `scp deploy@181.111.213.235`.
> Este ejemplo con `scp` es meramente ilustrativo. Mientras respete la ubicación y la convención de nombres, no importa el método que elija para copiar los certificados.

De esta forma, solo resta reiniciar el servicio `nginx`. Para esto necesita hacer login en el servidor y ejecutar:

```bash
cd web
make restart app=nginx
```

Alternativamente, desde un acceso remoto via `ssh`:

```
ssh -t deploy@environment "cd ~/web && make restart app=nginx"
```

> Reemplace `environment` con el nombre del entorno en su red, ej: `ssh deploy@181.111.213.235`.

Por último, puede consultar la [referencia de configuraciones](config-ref.md#nginxconf) para nginx.
