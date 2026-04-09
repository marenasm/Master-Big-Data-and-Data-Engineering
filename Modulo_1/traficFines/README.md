# traficFines

Paquete Python para la descarga, limpieza y análisis de datos de **multas de tráfico**
del Ayuntamiento de Madrid publicados en el [portal de datos abiertos](https://datos.madrid.es).

---

## Autores

| Nombre | Rol |
|--------|-----|
| Mateo | Autor principal |
| Claude Sonnet 4.6 (Anthropic) | Colaborador — asistencia en diseño, implementación, tests y documentación |

---

## Estructura del proyecto

```
traficFines/
├── traficFines/                    # Código fuente del paquete
│   ├── __init__.py                 # API pública: importaciones y __all__
│   ├── cache.py                    # Módulo de caché en disco
│   └── madridFines.py              # Módulo principal de multas
├── tests/                          # Suite de tests unitarios
│   ├── data/                       # Directorio de caché exclusivo para tests
│   ├── conftest.py                 # Fixtures compartidas (mocks, CSV/HTML de muestra)
│   ├── test_cache.py               # Tests de Cache y CacheUrl (39 tests)
│   └── test_madridFines.py         # Tests de MadridFines y get_url (55 tests)
├── notebooks/
│   ├── etapa1_exploratorio.ipynb   # Análisis exploratorio inicial (Etapa 1)
│   └── demo_validacion.ipynb       # Demo y validación completa del paquete
├── enunciado.ipynb                 # Enunciado original de la práctica
├── setup.py                        # Script de instalación
├── pyproject.toml                  # Configuración del proyecto y pytest
└── README.md
```

---

## Instalación

### Opción 1 — Desde el fichero `.whl` (recomendado para uso)

```bash
pip install traficFines-1.0.0-py3-none-any.whl
```

### Opción 2 — Desde el código fuente

```bash
cd traficFines
pip install .
```

### Opción 3 — Con dependencias de desarrollo (incluye pytest)

```bash
cd traficFines
pip install ".[dev]"
```

### Opción 4 — Entorno virtual aislado (recomendado para desarrollo)

```bash
cd traficFines
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows
pip install ".[dev]"
```

---

## Uso rápido

```python
from traficFines import MadridFines, MadridError

# Crear instancia con caché local de 7 días
mf = MadridFines(app_name="mi_analisis", obsolescence=7)

# Cargar datos de un mes concreto
mf.add(2024, 12)
print(mf.loaded)       # [(12, 2024)]
print(mf.data.shape)   # (249801, 14)

# Cargar un mes adicional (no duplica si ya está cargado)
mf.add(2024, 11)

# Cargar un año completo (ignora los meses sin datos)
mf.add(2023)

# Análisis: distribución por calificación
cal = mf.fines_calification()
print(cal)

# Análisis: importes máximo y mínimo por mes
pago = mf.total_payment()
print(pago)

# Gráfico de multas por hora del día
mf.fines_hour("evolucion_multas.png")
```

---

## Descripción del código

### `traficFines/__init__.py` — Fachada del paquete

Marca la carpeta como paquete Python y re-exporta en la superficie todo lo necesario:

```python
from .cache import Cache, CacheUrl, CacheError
from .madridFines import MadridFines, MadridError, get_url
```

Gracias a esto el usuario importa directamente desde `traficFines` sin conocer
la estructura interna de módulos.  `__all__` define explícitamente la API pública.

---

### `traficFines/cache.py` — Caché en disco

Evita descargas repetidas guardando el contenido en ficheros locales.

#### `CacheError`
Excepción propia del módulo. Se lanza ante cualquier error de lectura, escritura
o acceso a disco, permitiendo al código cliente capturar solo los errores de caché
con un `except CacheError`.

#### `Cache`

Almacena cualquier texto bajo un identificador (nombre de fichero) en una
subcarpeta propia de la aplicación dentro de `~/.my_cache/<app_name>/`.

| Método | Descripción |
|--------|-------------|
| `set(name, data)` | Escribe `data` en disco con el nombre `name`. |
| `exists(name)` | `True` si el fichero existe en caché. |
| `load(name)` | Lee y devuelve el contenido. Lanza `CacheError` si no existe. |
| `how_old(name)` | Antigüedad del fichero en **milisegundos**. |
| `is_obsolete(name)` | `True` si la antigüedad supera `obsolescence` días. |
| `delete(name)` | Borra el fichero. No lanza error si no existe. |
| `clear()` | Borra todos los ficheros del directorio de caché. |

Los atributos `app_name`, `cache_dir` y `obsolescence` son de **solo lectura**
(decorados con `@property` sin setter).

```python
from traficFines import Cache, CacheError

cache = Cache(app_name="mi_app", base_dir="/tmp/cache", obsolescence=3)
cache.set("clave", "contenido de prueba")
print(cache.load("clave"))          # "contenido de prueba"
print(cache.how_old("clave"))       # ~0.5 ms
print(cache.is_obsolete("clave"))   # False (acaba de crearse)
cache.delete("clave")
```

#### `CacheUrl`

Especialización de `Cache` para URLs de Internet. Convierte cada URL en un
**hash MD5** de 32 caracteres antes de usarlo como nombre de fichero, evitando
caracteres inválidos en el sistema de ficheros (`?`, `=`, `/`, etc.).

| Método | Descripción |
|--------|-------------|
| `get(url)` | Descarga `url` si no está en caché o está obsoleta; si no, la lee del disco. |
| `exists(url)` | `True` si la URL está cacheada. |
| `load(url)` | Lee el contenido cacheado de la URL. |
| `how_old(url)` | Antigüedad en milisegundos del contenido de la URL. |
| `delete(url)` | Borra el fichero cacheado de la URL. |

```python
from traficFines import CacheUrl

cu = CacheUrl(app_name="mi_app", obsolescence=7)
# Primera llamada: descarga y guarda en disco
contenido = cu.get("https://httpbin.org/get")
# Segunda llamada: lee de disco (sin petición HTTP)
contenido2 = cu.get("https://httpbin.org/get")
assert contenido == contenido2
```

---

### `traficFines/madridFines.py` — Módulo principal

#### Constantes

```python
RAIZ = "https://datos.madrid.es"
MADRID_FINES_URL = "dataset/210104-0-multas-circulacion-detalle/downloads"
```

`_FULL_URL` es la página del portal donde se listan todos los CSV de multas
por mes. Es la URL sobre la que se realiza el scraping.

#### `MadridError`

Excepción propia del módulo. Agrupa todos los errores posibles (red, portal
caído, mes no encontrado, CSV corrupto) en un único tipo que el código cliente
puede capturar con `except MadridError`.

#### `get_url(year, month) -> str`

Realiza **scraping con BeautifulSoup** sobre la página de descargas del portal
para localizar la URL exacta del CSV de un mes y año concretos.

El portal lista cada recurso en un bloque `<div class="row g-0">`.  Hay dos
formatos de fecha en el texto según la antigüedad del dato:

| Tipo | Formato en el HTML |
|------|--------------------|
| Reciente (< 3 meses) | `"Detalle. Diciembre 2024"` — mes primero |
| Histórico | `"2024 Enero. Detalle"` — año primero |

La función busca el bloque cuyo texto contenga el nombre del mes **y** el año,
en cualquier orden, ignorando los bloques "Agrupadas-excluidas".

```python
from traficFines import get_url, MadridError

try:
    url = get_url(2024, 12)   # Funciona desde junio 2017 en adelante
    print(url)
except MadridError as e:
    print(f"Error: {e}")
```

#### `_hora_to_time(hora) -> tuple[int, int]`

Función auxiliar privada a nivel de módulo. Convierte la hora en formato
decimal del CSV (ej. `20.23`) en una tupla `(hora, minuto)` → `(20, 23)`.
Devuelve `(0, 0)` si el valor no es convertible (NaN, None, texto).

#### `MadridFines`

Clase principal. Gestiona el ciclo completo: descarga → limpieza → análisis.

**Constructor**

```python
mf = MadridFines(app_name="mi_analisis", obsolescence=7)
```

Crea un `CacheUrl` interno que guarda los CSV descargados durante `obsolescence`
días.  `data` (DataFrame) y `loaded` (lista de tuplas) empiezan vacíos y son
de **solo lectura** desde fuera.

**`_load(year, month, cacheurl)` — estático, interno**

1. Llama a `get_url(year, month)` para obtener la URL del CSV.
2. Usa `cacheurl.get(url)` para descargar o recuperar de caché.
3. Parsea el texto con `pd.read_csv` usando separador `;` y codificación `latin1`.
4. Devuelve el DataFrame crudo.

**`_clean(df)` — estático, interno**

Limpia y normaliza el DataFrame **en el sitio** (sin devolver nada):

1. Elimina espacios en los nombres de columnas.
2. Renombra `COORDENADA-X/Y` → `COORDENADA_X/Y` y `HECHO-BOL` → `HECHO_BOL`.
3. Elimina espacios en columnas de texto (`CALIFICACION`, `LUGAR`, etc.).
4. Convierte velocidades y coordenadas a numérico con `pd.to_numeric`.
5. Construye la columna `fecha` combinando `ANIO`, `MES` y `HORA` (decimal
   convertida a horas y minutos enteros), y la establece como índice.

**`add(year, month=None)`**

- Si `month` es `None`, itera del 1 al 12 ignorando los meses sin datos.
- Si el mes ya está en `loaded`, no hace nada (evita duplicados).
- Si hay que cargarlo: `_load` → `_clean` → `pd.concat` al DataFrame acumulado.

**`fines_hour(fig_name)`**

Genera un gráfico de líneas (una por mes cargado) mostrando la distribución
de multas a lo largo de las 24 horas del día. Guarda la imagen en `fig_name`.

**`fines_calification() -> pd.DataFrame`**

Tabla pivote con índice `(MES, ANIO)` y columnas `GRAVE`, `LEVE`, `MUY GRAVE`.

**`total_payment() -> pd.DataFrame`**

DataFrame con `importe_maximo` (todos pagan sin descuento) e `importe_minimo`
(todos acogen el descuento del 50% por pronto pago), agrupado por `(MES, ANIO)`.

---

## Ejecución del paquete paso a paso

### 1. Preparar el entorno

```bash
cd traficFines
python -m venv .venv
source .venv/bin/activate       # Linux / macOS
pip install ".[dev]"
```

### 2. Ejecutar los tests

```bash
# Tests simples
pytest

# Tests con cobertura detallada
pytest --cov=traficFines --cov-report=term-missing

# Solo un módulo
pytest tests/test_cache.py -v
pytest tests/test_madridFines.py -v
```

### 3. Usar el paquete en un script Python

```python
from traficFines import MadridFines, MadridError

mf = MadridFines()
mf.add(2024, 12)
print(mf.data.head())
print(mf.fines_calification())
mf.fines_hour("grafico.png")
```

### 4. Usar el paquete en Jupyter

```bash
# Instalar Jupyter en el entorno
pip install jupyter

# Lanzar Jupyter desde la raíz del proyecto
jupyter notebook notebooks/demo_validacion.ipynb
```

El notebook `demo_validacion.ipynb` recorre todas las funcionalidades del
paquete con ejemplos ejecutables celda a celda.

### 5. Generar el fichero `.whl` para distribución

```bash
pip install build
python -m build --wheel
# El fichero .whl aparece en dist/traficFines-1.0.0-py3-none-any.whl
```

---

## Módulos y API pública

### `traficFines.cache`

| Clase / Excepción | Descripción |
|---|---|
| `CacheError` | Excepción base del módulo. |
| `Cache` | Almacena y recupera datos en disco por nombre. |
| `CacheUrl` | Especialización de `Cache` para URLs (usa hash MD5 como clave). |

### `traficFines.madridFines`

| Elemento | Descripción |
|---|---|
| `MadridError` | Excepción base del módulo. |
| `get_url(year, month)` | Scraping del portal → URL del CSV del mes solicitado. |
| `MadridFines` | Ciclo completo: descarga, limpieza y análisis de multas. |

---

## Tests

La suite tiene **94 tests** con cobertura cercana al 100%.

```bash
pytest --cov=traficFines --cov-report=term-missing
```

- Todos los accesos a Internet se simulan con `unittest.mock` — los tests
  funcionan **sin conexión**.
- Los ficheros de caché se crean en directorios temporales (`tmp_path` de pytest)
  y se eliminan automáticamente al terminar cada test.
- El directorio `tests/data/` existe para fixtures de datos persistentes.

---

## Requisitos

| Librería | Versión mínima | Uso |
|----------|---------------|-----|
| Python | >= 3.11 | Anotaciones de tipo modernas (`list[tuple[...]]`) |
| pandas | >= 2.0 | Manipulación de DataFrames |
| requests | >= 2.28 | Peticiones HTTP al portal de Madrid |
| beautifulsoup4 | >= 4.12 | Scraping HTML de la página de descargas |
| matplotlib | >= 3.7 | Generación de gráficos |
| numpy | >= 1.24 | Operaciones numéricas |

Dependencias de desarrollo adicionales: `pytest >= 7.4`, `pytest-cov >= 4.1`.

---

## Notas importantes

- Los datos están disponibles desde **junio de 2017** en adelante.
- El portal de Madrid puede cambiar su estructura HTML con el tiempo.
  La URL de scraping actual es:
  `https://datos.madrid.es/dataset/210104-0-multas-circulacion-detalle/downloads`
- La columna de coordenadas puede llamarse `COORDENADA-X/Y` (guion) o
  `COORDENADA_X/Y` (guion bajo) según el año; el módulo normaliza ambas.
- El método `add()` nunca duplica meses ya cargados.
- La caché por defecto tiene una validez de **7 días**; pasado ese tiempo
  se descarga de nuevo automáticamente.