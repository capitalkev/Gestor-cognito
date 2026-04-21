# Guía de dependencias por ambiente + PyTest (Python)

Esta guía documenta una estrategia simple y reproducible para separar dependencias de **runtime** (la aplicación) y de **test** (PyTest y tooling), y para ejecutar tests en un paso común del pipeline. Si necesitas separación por ambiente (dev/staging/prod), puedes agregar archivos adicionales por entorno (ver más abajo).

---

## Objetivos

* Mantener entornos **limpios**, sin herramientas de prueba en imágenes/productivo.
* Permitir que **todos** los despliegues (dev, homologación/staging, prod) ejecuten el mismo **step de tests**.
* Facilitar **reproducibilidad** y **cacheo** de dependencias.

---

## Estructura de archivos

```
requirements/
  requirements.txt  # dependencias de runtime (app)
  tests.txt         # dependencias de test y tooling (incluye -r requirements.txt)
```

**Notas:**

* `requirements/requirements.txt` contiene lo necesario para ejecutar la aplicación.
* `requirements/tests.txt` hereda runtime vía `-r requirements.txt` y agrega herramientas de test/calidad.

---

## Instalación por entorno

```bash
# Instalar dependencias de runtime
pip install -r requirements/requirements.txt

# Instalar dependencias de test (sólo para el step de tests)
pip install -r requirements/tests.txt

# Ejecutar tests
pytest -q
```

---

## Con Docker (multi-stage)

Mantén la imagen final sin PyTest, pero ejecútalo antes.

```dockerfile
# Etapa de test
FROM python:3.12-slim AS test
WORKDIR /app
COPY requirements/ requirements/
RUN pip install -r requirements/requirements.txt \
 && pip install -r requirements/tests.txt
COPY . .
RUN pytest -q

# Etapa de runtime (limpia)
FROM python:3.12-slim AS runtime
WORKDIR /app
COPY requirements/ requirements/
RUN pip install -r requirements/requirements.txt
COPY . .
CMD ["gunicorn", "app.wsgi:application", "-b", "0.0.0.0:8000"]
```

> **Tip:** Si necesitas diferencias por ambiente, crea `dev.txt`/`prod.txt`/`staging.txt` que hagan `-r requirements.txt` y agreguen sólo los extras del entorno.

---

## Alternativas y mejoras

### `pip-tools` (reproducibilidad)

Usa ficheros fuente (`.in`) y compílalos a `.txt` bloqueados.

```
requirements/
  requirements.in  # fuente de runtime (app)
  tests.in         # fuente de tests/tooling (puede incluir: -r requirements.in)
  # (opcional) dev.in / prod.in / staging.in -> -r requirements.in + extras del entorno
```

Compilar:

```bash
pip install pip-tools
pip-compile requirements/requirements.in -o requirements/requirements.txt
pip-compile requirements/tests.in -o requirements/tests.txt
```

### Extras en `pyproject.toml`

Alternativa si empaquetas el proyecto.

```toml
[project]
name = "mi-paquete"
version = "0.1.0"

[project.optional-dependencies]
test = [
  "pytest",
  "pytest-cov",
  "pytest-django",
]
```

Instalación en CI:

```bash
pip install -r requirements/requirements.txt
pip install -e .[test]
pytest -q
```

### `tox`/`nox` (estandarizar comandos y matrices)

Ejemplo `tox.ini`:

```ini
[tox]
envlist = py312

[testenv]
deps = -r requirements/tests.txt
commands = pytest -q
```

---

## Buenas prácticas

* **No mezclar** dependencias de test con runtime en imágenes finales.
* Usar `-r requirements.txt` para **herencia** (por ejemplo en `tests.txt` o en ficheros por ambiente) y evitar duplicar versiones.
* **Fijar versiones** (y actualizar con intención) para reproducibilidad.
* **Cachear** el directorio de pip en CI para acelerar pipelines.
* Mantener staging **lo más cercano posible** a prod para validar el runtime real.
* Publicar reportes de test/coverage como artefactos si el CI lo permite.

---

## Preguntas frecuentes (FAQ)

**¿Por qué no usar `pip install -r requirements.*.txt`?**  Mezcla listas y contamina entornos con dependencias no deseadas, dificultando la depuración y el cache.

**¿Dónde instalo `pytest` en prod?**  En ninguna parte: se instala **sólo en el step de CI** o etapa de tests. La imagen final no debe incluirlo.

**¿Staging necesita `gunicorn`?**  Sí, si replica prod. Agrega el server WSGI/ASGI correspondiente al archivo de runtime que uses en ese ambiente.

**¿Cómo ejecuto tests localmente?**

```bash
pip install -r requirements/requirements.txt
pip install -r requirements/tests.txt
pytest -q
```

---

## Checklist de adopción

* [ ] Mantener `requirements/requirements.txt` como runtime de la app.
* [ ] Mantener `requirements/tests.txt` para CI y ejecución local de tests.
* [ ] (Opcional) Agregar ficheros por entorno (`dev.txt`, `prod.txt`, etc.) si necesitas diferencias de runtime.
* [ ] Actualizar pipeline para instalar `requirements.txt` + `tests.txt` y luego ejecutar `pytest`.
* [ ] (Opcional) Implementar `pip-tools` o `tox` para mayor control.
* [ ] Habilitar caché de pip en el CI.

---

**Fin.**
