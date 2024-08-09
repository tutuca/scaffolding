# Nuevas versiones

---

## Registrar cambios

Anotar todos los MR integrados posteriores a la última versión, y los issues que hayan sido cerrados en el archivo `CHANGELOG.md` en la seccion **Untagged**.

Ejemplo:

```markdown
#### Untagged

- #111 Mejoras en el login de usuarios.
- #107 Galería de imágenes
```

## Nueva release/version

Crear una rama `release`. En caso de que exista, primero eliminar la misma:

```bash
git branch -D release
git checkout -b release
git merge develop
```

Actualizar número de versión, según [versionado semántico](https://semver.org/lang/es/#resumen).

> `major` para cambios grandes.
>
> `minor` para mejoras incrementales.
>
> `patch` para bugfixes.

Ejecutar comando que corresponda:

```bash
# patch
bumpversion patch --commit

# minor
bumpversion minor --commit

# major
bumpversion major --commit

# Estos comandos actualizaran el numero de la version en distintos archivos,
# para mas info ver archivo `.bumpversion.cfg`
```

En el archivo `CHANGELOG.md`, mover el contenido de la seccion `Untagged` a una nueva seccion/heading correspondiente a la nueva release/version que contenga el siguiente formato:

> `[version] fecha`
>
> `#issue_number issue_description`

Ejemplo:

```
## [0.3.0] 01-02-2020

- #111 Mejoras en el login de usuarios.
- #107 Galería de imágenes
```

Actualizar el commit de versión con el `CHANGELOG`

```bash
git commit CHANGELOG --amend
```

Integrar en `develop`, localmente:

```bash
git checkout develop
git merge release
git branch -D release
git push
```

## Integrar version a `main` branch

Ahora que la nueva versión está lista para ser desplegada, sincronizar con la rama `main`.

```bash
git checkout main
git merge develop
git push
```
