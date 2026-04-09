"""
conftest.py
===========
Fixtures compartidas para todos los tests del paquete traficFines.
Los accesos a Internet y al sistema de ficheros se simulan con mocks.
El directorio de caché de prueba se crea dentro de tests/data/.
"""

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Directorio de datos de tests (dentro de tests/data/)
# ---------------------------------------------------------------------------

TESTS_DIR = Path(__file__).parent
DATA_DIR = TESTS_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


@pytest.fixture
def test_cache_dir(tmp_path):
    """Devuelve un directorio temporal limpio para cada test."""
    return tmp_path / "cache"


# ---------------------------------------------------------------------------
# CSV de muestra (diciembre 2024, 5 filas)
# ---------------------------------------------------------------------------

SAMPLE_CSV = textwrap.dedent("""\
    CALIFICACION ;LUGAR                ;MES;ANIO;HORA ;IMP_BOL;DESCUENTO;PUNTOS;DENUNCIANTE;HECHO-BOL           ;VEL_LIMITE ;VEL_CIRCULA ;COORDENADA-X ;COORDENADA-Y \n\
    LEVE         ;CL CLARA DEL REY 36 ;12 ;2024;20.23;60.0   ;SI       ;0     ;SER        ;ESTACIONAR          ;           ;            ;             ;            \n\
    LEVE         ;CL CLARA DEL REY 28 ;12 ;2024;20.27;90.0   ;SI       ;0     ;SER        ;ESTACIONAR SIN AUT  ;           ;            ;             ;            \n\
    GRAVE        ;CL CANILLAS 63      ;12 ;2024;20.45;200.0  ;SI       ;0     ;SER        ;ESTACIONAR OBSTAC   ;           ;            ;             ;            \n\
    LEVE         ;CL BRAVO MURILLO 24 ;12 ;2024;16.30;60.0   ;SI       ;0     ;SER        ;ESTACIONAR CON AUT  ;           ;            ;             ;            \n\
    MUY GRAVE    ;CL BRAVO MURILLO 16 ;12 ;2024;16.50;500.0  ;NO       ;4     ;POLICIA    ;EXCESO VELOCIDAD    ;50         ;90          ;440123.0     ;4474321.0   \n\
""")


@pytest.fixture
def sample_csv():
    """Devuelve el contenido CSV de muestra como string."""
    return SAMPLE_CSV


# ---------------------------------------------------------------------------
# HTML de muestra que simula la página del portal de Madrid
# ---------------------------------------------------------------------------

SAMPLE_HTML = """
<html><body>
<a href="/egob/catalogo/210104-395-multas-circulacion-detalle.csv">diciembre 2024</a>
<a href="/egobfiles/MANUAL/210104/202412detalle.csv">diciembre 2024 directo</a>
<a href="/egobfiles/MANUAL/210104/201706detalle.csv">junio 2017</a>
<a href="/egobfiles/MANUAL/210104/202305detalle.csv">mayo 2023</a>
</body></html>
"""


@pytest.fixture
def sample_html():
    """Devuelve el HTML de muestra como string."""
    return SAMPLE_HTML


# ---------------------------------------------------------------------------
# Mock de requests.get
# ---------------------------------------------------------------------------

def make_mock_response(text: str, status_code: int = 200):
    """Crea un objeto mock que imita requests. Response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = text
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        import requests
        mock.raise_for_status.side_effect = requests.HTTPError(
            f"HTTP {status_code}"
        )
    return mock


@pytest.fixture
def mock_requests_html(sample_html):
    """Parchea requests.get para devolver el HTML de muestra."""
    with patch("traficFines.madridFines.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(sample_html)
        yield mock_get


@pytest.fixture
def mock_requests_csv(sample_csv):
    """Parchea requests.get para devolver el CSV de muestra."""
    with patch("traficFines.cache.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(sample_csv)
        yield mock_get
