"""
test_madridFines.py
===================
Tests unitarios para ``get_url`` y la clase ``MadridFines`` del módulo
``traficFines.madridFines``.

Todos los accesos a Internet se simulan con mocks.
Los ficheros de caché se almacenan en directorios temporales (tmp_path).
"""

import io
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests as req

from traficFines.madridFines import (
    MadridFines,
    MadridError,
    get_url,
    RAIZ,
)
from traficFines.cache import CacheUrl, CacheError


# ===========================================================================
# Datos de muestra compartidos
# ===========================================================================

# HTML de muestra que simula la página de descargas del nuevo portal de Madrid.
# Cada recurso aparece en un <div class="row g-0"> con el nombre del mes/año
# en el texto y un enlace de descarga directa al CSV.
SAMPLE_HTML_WITH_LINKS = """
<html><body>
<div class="row g-0">
  CSVDetalle. Diciembre 2024
  <a href="/dataset/210104-0/resource/r15/download/202412detalle.csv">Descarga</a>
</div>
<div class="row g-0">
  CSVAgrupadas-excluidas. Diciembre 2024
  <a href="/dataset/210104-0/resource/r15ag/download/202412agrupadas.csv">Descarga</a>
</div>
<div class="row g-0">
  CSVDetalle. Junio 2017
  <a href="/dataset/210104-0/resource/r06/download/201706detalle.csv">Descarga</a>
</div>
<div class="row g-0">
  CSVDetalle. Mayo 2023
  <a href="/dataset/210104-0/resource/r23/download/202305detalle.csv">Descarga</a>
</div>
</body></html>
"""

# CSV con 5 filas: 3 LEVE, 1 GRAVE, 1 MUY GRAVE en mes 12/2024
SAMPLE_CSV_DEC24 = (
    "CALIFICACION ;LUGAR                ;MES;ANIO;HORA ;IMP_BOL;DESCUENTO;PUNTOS;DENUNCIANTE;HECHO-BOL         ;VEL_LIMITE ;VEL_CIRCULA ;COORDENADA-X ;COORDENADA-Y \n"
    "LEVE         ;CL CLARA DEL REY 36 ;12 ;2024;20.23;60.0   ;SI       ;0     ;SER        ;ESTACIONAR        ;           ;            ;             ;            \n"
    "LEVE         ;CL CLARA DEL REY 28 ;12 ;2024;20.27;90.0   ;SI       ;0     ;SER        ;ESTACIONAR SIN AUT;           ;            ;             ;            \n"
    "GRAVE        ;CL CANILLAS 63      ;12 ;2024;20.45;200.0  ;SI       ;0     ;SER        ;ESTACIONAR OBSTAC ;           ;            ;             ;            \n"
    "LEVE         ;CL BRAVO MURILLO 24 ;12 ;2024;16.30;60.0   ;SI       ;0     ;SER        ;ESTACIONAR CON AUT;           ;            ;             ;            \n"
    "MUY GRAVE    ;CL BRAVO MURILLO 16 ;12 ;2024;16.50;500.0  ;NO       ;4     ;POLICIA    ;EXCESO VELOCIDAD  ;50         ;90          ;440123.0     ;4474321.0   \n"
)

SAMPLE_CSV_NOV24 = (
    "CALIFICACION ;LUGAR        ;MES;ANIO;HORA ;IMP_BOL;DESCUENTO;PUNTOS;DENUNCIANTE;HECHO-BOL   ;VEL_LIMITE ;VEL_CIRCULA ;COORDENADA-X ;COORDENADA-Y \n"
    "GRAVE        ;CL ALCALA 10 ;11 ;2024;10.00;200.0  ;SI       ;0     ;SER        ;INFRACCION  ;           ;            ;             ;            \n"
)

SAMPLE_CSV_COORD_UNDERSCORE = (
    "CALIFICACION ;LUGAR   ;MES;ANIO;HORA ;IMP_BOL;DESCUENTO;PUNTOS;DENUNCIANTE;HECHO-BOL ;VEL_LIMITE;VEL_CIRCULA;COORDENADA_X;COORDENADA_Y\n"
    "LEVE         ;CL A 1  ;5  ;2019;9.00 ;60.0   ;SI       ;0     ;SER        ;ESTACIONAR;           ;           ;440000.0    ;4470000.0  \n"
)


def _df_from_csv(csv_str: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(csv_str), sep=";", encoding="latin1")


def make_mock_response(text="", status_code=200):
    mock = MagicMock()
    mock.text = text
    mock.status_code = status_code
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        mock.raise_for_status.side_effect = req.HTTPError(f"HTTP {status_code}")
    return mock


# ===========================================================================
# Fixture: MadridFines con _load parcheado
# ===========================================================================

def _make_mf_with_mock_load(csv_str: str, year: int = 2024, month: int = 12):
    """
    Devuelve un objeto MadridFines cuyo método estático _load
    ha sido reemplazado por uno que devuelve directamente un DataFrame
    creado a partir de csv_str, sin ningún acceso a red.
    """
    df = _df_from_csv(csv_str)

    def mock_load(y, m, cacheurl):
        return df.copy()

    mf = MadridFines(app_name="test_app", obsolescence=1)
    mf._load = mock_load   # reemplazamos el static a nivel de instancia
    return mf


# ===========================================================================
# Tests de get_url
# ===========================================================================

class TestGetUrl:

    def test_mes_invalido_lanza_madriderror(self):
        with pytest.raises(MadridError):
            get_url(2024, 0)
        with pytest.raises(MadridError):
            get_url(2024, 13)

    def test_anio_anterior_2017_lanza_madriderror(self):
        with pytest.raises(MadridError):
            get_url(2016, 6)

    def test_url_encontrada_por_patron_yyyymm(self):
        with patch("traficFines.madridFines.requests.get") as mock_get:
            mock_get.return_value = make_mock_response(SAMPLE_HTML_WITH_LINKS)
            url = get_url(2024, 12)
        assert "202412" in url
        assert url.startswith("http")

    def test_url_encontrada_por_texto_enlace(self):
        with patch("traficFines.madridFines.requests.get") as mock_get:
            mock_get.return_value = make_mock_response(SAMPLE_HTML_WITH_LINKS)
            url = get_url(2017, 6)
        assert url.startswith("http")
        assert "201706" in url

    def test_mes_no_encontrado_lanza_madriderror(self):
        html_sin_datos = "<html><body><p>Sin recursos</p></body></html>"
        with patch("traficFines.madridFines.requests.get") as mock_get:
            mock_get.return_value = make_mock_response(html_sin_datos)
            with pytest.raises(MadridError):
                get_url(2024, 3)

    def test_error_de_red_lanza_madriderror(self):
        with patch(
            "traficFines.madridFines.requests.get",
            side_effect=req.RequestException("timeout"),
        ):
            with pytest.raises(MadridError):
                get_url(2024, 12)


# ===========================================================================
# Tests de MadridFines.__init__
# ===========================================================================

class TestMadridFinesInit:

    def test_data_inicial_vacio(self):
        mf = MadridFines()
        assert mf.data.empty
        assert mf.loaded == []

    def test_data_solo_lectura(self):
        mf = MadridFines()
        with pytest.raises(AttributeError):
            mf.data = pd.DataFrame()

    def test_loaded_solo_lectura(self):
        mf = MadridFines()
        with pytest.raises(AttributeError):
            mf.loaded = []

    def test_loaded_devuelve_copia(self):
        mf = MadridFines()
        lista = mf.loaded
        lista.append((1, 2000))
        assert (1, 2000) not in mf.loaded


# ===========================================================================
# Tests de _clean (estático)
# ===========================================================================

class TestClean:

    def test_limpia_espacios_columnas(self):
        df = _df_from_csv(SAMPLE_CSV_DEC24)
        MadridFines._clean(df)
        assert all(col == col.strip() for col in df.columns)

    def test_crea_indice_fecha(self):
        df = _df_from_csv(SAMPLE_CSV_DEC24)
        MadridFines._clean(df)
        assert df.index.name == "fecha"
        assert pd.api.types.is_datetime64_any_dtype(df.index)

    def test_renombra_coordenadas_guion(self):
        df = _df_from_csv(SAMPLE_CSV_DEC24)
        MadridFines._clean(df)
        assert "COORDENADA_X" in df.columns
        assert "COORDENADA_Y" in df.columns
        assert "COORDENADA-X" not in df.columns

    def test_coordenadas_underscore_sin_cambio(self):
        df = _df_from_csv(SAMPLE_CSV_COORD_UNDERSCORE)
        MadridFines._clean(df)
        assert "COORDENADA_X" in df.columns
        assert "COORDENADA_Y" in df.columns

    def test_columnas_numericas(self):
        df = _df_from_csv(SAMPLE_CSV_DEC24)
        MadridFines._clean(df)
        assert pd.api.types.is_float_dtype(df["VEL_CIRCULA"])
        assert pd.api.types.is_float_dtype(df["VEL_LIMITE"])

    def test_calificacion_sin_espacios(self):
        df = _df_from_csv(SAMPLE_CSV_DEC24)
        MadridFines._clean(df)
        for val in df["CALIFICACION"].dropna():
            assert val == val.strip()

    def test_hecho_bol_renombrado(self):
        df = _df_from_csv(SAMPLE_CSV_DEC24)
        MadridFines._clean(df)
        assert "HECHO_BOL" in df.columns
        assert "HECHO-BOL" not in df.columns


# ===========================================================================
# Tests de add() — _load mockeado a nivel de instancia
# ===========================================================================

class TestAdd:

    def test_add_mes_simple(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        assert not mf.data.empty
        assert (12, 2024) in mf.loaded
        assert len(mf.data) == 5

    def test_add_no_duplica_mes(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        filas_antes = len(mf.data)
        mf.add(2024, 12)
        assert len(mf.data) == filas_antes
        assert mf.loaded.count((12, 2024)) == 1

    def test_add_dos_meses_concatena(self):
        df_dec = _df_from_csv(SAMPLE_CSV_DEC24)
        df_nov = _df_from_csv(SAMPLE_CSV_NOV24)

        call_counter = {"n": 0}

        def mock_load(y, m, cacheurl):
            call_counter["n"] += 1
            if m == 12:
                return df_dec.copy()
            return df_nov.copy()

        mf = MadridFines(app_name="test_app", obsolescence=1)
        mf._load = mock_load

        mf.add(2024, 12)
        mf.add(2024, 11)

        assert (12, 2024) in mf.loaded
        assert (11, 2024) in mf.loaded
        assert len(mf.data) == 6

    def test_add_anio_completo_ignora_meses_sin_datos(self):
        df_dec = _df_from_csv(SAMPLE_CSV_DEC24)

        def mock_load(y, m, cacheurl):
            if m == 12:
                return df_dec.copy()
            raise MadridError(f"Mes {m} no disponible")

        mf = MadridFines(app_name="test_app", obsolescence=1)
        mf._load = mock_load
        mf.add(2024, None)  # año completo

        assert (12, 2024) in mf.loaded
        assert len(mf.loaded) == 1  # solo diciembre disponible

    def test_add_mes_no_disponible_lanza_madriderror(self):
        def mock_load(y, m, cacheurl):
            raise MadridError("URL no encontrada")

        mf = MadridFines(app_name="test_app", obsolescence=1)
        mf._load = mock_load

        with pytest.raises(MadridError):
            mf.add(2024, 12)

    def test_data_no_modificable_desde_fuera(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        with pytest.raises(AttributeError):
            mf.data = pd.DataFrame()


# ===========================================================================
# Tests de fines_hour()
# ===========================================================================

class TestFinesHour:

    def test_genera_fichero(self, tmp_path):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        fig_path = tmp_path / "test_hora.png"
        mf.fines_hour(str(fig_path))
        assert fig_path.exists()
        assert fig_path.stat().st_size > 0

    def test_sin_datos_lanza_madriderror(self):
        mf = MadridFines()
        with pytest.raises(MadridError):
            mf.fines_hour("test.png")

    def test_multiples_meses_genera_fichero(self, tmp_path):
        df_dec = _df_from_csv(SAMPLE_CSV_DEC24)
        df_nov = _df_from_csv(SAMPLE_CSV_NOV24)

        def mock_load(y, m, cacheurl):
            return df_dec.copy() if m == 12 else df_nov.copy()

        mf = MadridFines(app_name="test_app", obsolescence=1)
        mf._load = mock_load
        mf.add(2024, 12)
        mf.add(2024, 11)

        fig_path = tmp_path / "multi_hora.png"
        mf.fines_hour(str(fig_path))
        assert fig_path.exists()


# ===========================================================================
# Tests de fines_calification()
# ===========================================================================

class TestFinesCalification:

    def test_sin_datos_lanza_madriderror(self):
        mf = MadridFines()
        with pytest.raises(MadridError):
            mf.fines_calification()

    def test_devuelve_dataframe(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        result = mf.fines_calification()
        assert isinstance(result, pd.DataFrame)

    def test_columnas_calificaciones(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        result = mf.fines_calification()
        assert "LEVE" in result.columns
        assert "GRAVE" in result.columns
        assert "MUY GRAVE" in result.columns

    def test_indice_mes_anio(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        result = mf.fines_calification()
        assert result.index.names == ["MES", "ANIO"]

    def test_conteo_correcto(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        result = mf.fines_calification()
        # CSV tiene: 3 LEVE, 1 GRAVE, 1 MUY GRAVE en mes 12/2024
        row = result.loc[(12, 2024)]
        assert row["LEVE"] == 3
        assert row["GRAVE"] == 1
        assert row["MUY GRAVE"] == 1


# ===========================================================================
# Tests de total_payment()
# ===========================================================================

class TestTotalPayment:

    def test_sin_datos_lanza_madriderror(self):
        mf = MadridFines()
        with pytest.raises(MadridError):
            mf.total_payment()

    def test_devuelve_dataframe(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        result = mf.total_payment()
        assert isinstance(result, pd.DataFrame)

    def test_columnas_pago(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        result = mf.total_payment()
        assert "importe_maximo" in result.columns
        assert "importe_minimo" in result.columns

    def test_importe_minimo_es_mitad_maximo(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        result = mf.total_payment()
        row = result.loc[(12, 2024)]
        assert row["importe_minimo"] == pytest.approx(row["importe_maximo"] * 0.5)

    def test_indice_mes_anio(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        result = mf.total_payment()
        assert result.index.names == ["MES", "ANIO"]

    def test_importe_total_correcto(self):
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        result = mf.total_payment()
        # CSV: 60 + 90 + 200 + 60 + 500 = 910
        row = result.loc[(12, 2024)]
        assert row["importe_maximo"] == pytest.approx(910.0)
        assert row["importe_minimo"] == pytest.approx(455.0)


# ===========================================================================
# Tests de cobertura adicional para madridFines.py
# ===========================================================================

class TestGetUrlCoverage:
    """Cubre href absoluto en el enlace de descarga."""

    def test_url_con_href_absoluto(self):
        """Enlace de descarga con href ya absoluto se devuelve tal cual."""
        html = """
        <html><body>
        <div class="row g-0">
          CSVDetalle. Diciembre 2024
          <a href="https://datos.madrid.es/dataset/r15/download/202412detalle.csv">Descarga</a>
        </div>
        </body></html>
        """
        with patch("traficFines.madridFines.requests.get") as mock_get:
            mock_get.return_value = make_mock_response(html)
            url = get_url(2024, 12)
        assert url.startswith("https://")
        assert "202412" in url


class TestLoadCoverage:
    """Cubre los bloques de error en MadridFines._load."""

    def test_load_cache_error_lanza_madriderror(self):
        """CacheError en cacheurl.get() se convierte a MadridError."""
        mock_cache = MagicMock()
        mock_cache.get.side_effect = CacheError("fallo de red")

        with patch("traficFines.madridFines.get_url", return_value="https://fake.url"):
            with pytest.raises(MadridError, match="Error al descargar datos"):
                MadridFines._load(2024, 12, mock_cache)

    def test_load_csv_malformado_lanza_madriderror(self):
        """CSV no parseable lanza MadridError."""
        mock_cache = MagicMock()
        # Simulamos que read_csv lanza error devolviendo contenido que lo provoque
        mock_cache.get.return_value = "contenido_invalido\x00\x00\x00"

        with patch("traficFines.madridFines.get_url", return_value="https://fake.url"):
            with patch("traficFines.madridFines.pd.read_csv",
                       side_effect=Exception("CSV error")):
                with pytest.raises(MadridError, match="Error al parsear"):
                    MadridFines._load(2024, 12, mock_cache)


class TestCleanEdgeCases:
    """Cubre ramas de _clean con datos edge-case."""

    def test_hora_invalida_devuelve_cero(self):
        """Valores de HORA no convertibles se tratan como hora 0."""
        csv = (
            "CALIFICACION;LUGAR;MES;ANIO;HORA;IMP_BOL;DESCUENTO;PUNTOS;DENUNCIANTE;HECHO-BOL;VEL_LIMITE;VEL_CIRCULA;COORDENADA-X;COORDENADA-Y\n"
            "LEVE;CL A;12;2024;NA;60.0;SI;0;SER;EST;;;;\n"
        )
        df = pd.read_csv(io.StringIO(csv), sep=";", encoding="latin1")
        MadridFines._clean(df)
        assert df.index.name == "fecha"

    def test_columna_fecha_redundante_eliminada(self):
        """Si 'fecha' aparece como columna Y como índice, se elimina la columna."""
        csv = (
            "CALIFICACION;LUGAR;MES;ANIO;HORA;IMP_BOL;DESCUENTO;PUNTOS;DENUNCIANTE;HECHO-BOL;VEL_LIMITE;VEL_CIRCULA;COORDENADA-X;COORDENADA-Y\n"
            "LEVE;CL A;12;2024;10.0;60.0;SI;0;SER;EST;;;;\n"
        )
        df = pd.read_csv(io.StringIO(csv), sep=";", encoding="latin1")
        # Añadir columna 'fecha' artificial para forzar la rama de eliminación
        df["fecha"] = pd.Timestamp("2024-12-01")
        MadridFines._clean(df)
        assert "fecha" not in df.columns


class TestTotalPaymentEdge:
    """Cubre la rama de IMP_BOL ausente."""

    def test_sin_imp_bol_lanza_madriderror(self):
        mf = MadridFines()
        # Inyectamos un DataFrame sin IMP_BOL
        df = pd.DataFrame({"MES": [12], "ANIO": [2024], "CALIFICACION": ["LEVE"]})
        df.index.name = "fecha"
        mf._data = df
        mf._loaded = [(12, 2024)]
        with pytest.raises(MadridError, match="IMP_BOL"):
            mf.total_payment()


class TestGetUrlTextFallback:
    """Cubre href relativo en el enlace de descarga."""

    def test_texto_con_href_relativo(self):
        """Enlace con href relativo se convierte a URL absoluta con RAIZ."""
        html = """
        <html><body>
        <div class="row g-0">
          CSVDetalle. Junio 2017
          <a href="/dataset/r06/download/201706detalle.csv">Descarga</a>
        </div>
        </body></html>
        """
        with patch("traficFines.madridFines.requests.get") as mock_get:
            mock_get.return_value = make_mock_response(html)
            url = get_url(2017, 6)
        assert url.startswith("http")
        assert "201706" in url


class TestFinesHourEmptySubset:
    """Cubre la rama 'subset.empty' en fines_hour."""

    def test_subset_vacio_salta_linea(self, tmp_path):
        """Si un mes cargado no tiene filas que coincidan, se salta silenciosamente."""
        mf = _make_mf_with_mock_load(SAMPLE_CSV_DEC24)
        mf.add(2024, 12)
        # Manipulamos _loaded para incluir un mes que no existe en _data
        mf._loaded.append((1, 2024))
        fig_path = tmp_path / "test_vacio.png"
        # No debe lanzar excepción
        mf.fines_hour(str(fig_path))
        assert fig_path.exists()


class TestGetUrlAbsoluteTextHref:
    """Cubre que los bloques 'Agrupadas' son ignorados aunque coincidan en mes/año."""

    def test_agrupadas_son_ignoradas(self):
        """Un bloque Agrupadas-excluidas no se devuelve aunque coincida en mes/año."""
        html = """
        <html><body>
        <div class="row g-0">
          CSVAgrupadas-excluidas. Diciembre 2024
          <a href="/dataset/r15ag/download/202412agrupadas.csv">Descarga</a>
        </div>
        </body></html>
        """
        with patch("traficFines.madridFines.requests.get") as mock_get:
            mock_get.return_value = make_mock_response(html)
            with pytest.raises(MadridError):
                get_url(2024, 12)


class TestLoadGetUrlError:
    """Cubre la rama donde get_url lanza MadridError en _load."""

    def test_get_url_error_propaga_madriderror(self):
        mock_cache = MagicMock()
        with patch("traficFines.madridFines.get_url",
                   side_effect=MadridError("URL no encontrada")):
            with pytest.raises(MadridError, match="URL no encontrada"):
                MadridFines._load(2024, 12, mock_cache)


class TestCleanFechaRedundante:
    """Cubre la eliminación de columna 'fecha' redundante en _clean."""

    def test_sin_columnas_fecha_anio_mes_no_falla(self):
        """Si no existen columnas ANIO/MES/HORA, _clean no debe lanzar error."""
        df = pd.DataFrame({
            "CALIFICACION": ["LEVE"],
            "LUGAR": ["CL A 1"],
            "IMP_BOL": [60.0],
        })
        # No debe lanzar excepción aunque falten las columnas de fecha
        MadridFines._clean(df)
        assert "CALIFICACION" in df.columns


class TestGetUrlTextRelativeHref:
    """Cubre href relativo construido con RAIZ en bloque con texto del mes."""

    def test_texto_con_href_relativo_construye_url_absoluta(self):
        """La URL absoluta se construye correctamente a partir de href relativo."""
        html = """
        <html><body>
        <div class="row g-0">
          CSVDetalle. Mayo 2023
          <a href="/dataset/r23/download/202305detalle.csv">Descarga</a>
        </div>
        </body></html>
        """
        with patch("traficFines.madridFines.requests.get") as mock_get:
            mock_get.return_value = make_mock_response(html)
            url = get_url(2023, 5)
        assert url.startswith("https://")
        assert "202305" in url


class TestLoadCSVParseError:
    """Cubre la rama except Exception en pd.read_csv (línea 237)."""

    def test_read_csv_exception_lanza_madriderror(self):
        mock_cache = MagicMock()
        mock_cache.get.return_value = "col1;col2\nv1;v2"

        with patch("traficFines.madridFines.get_url", return_value="https://fake.url"):
            with patch("traficFines.madridFines.pd.read_csv",
                       side_effect=ValueError("parse error")):
                with pytest.raises(MadridError, match="Error al parsear"):
                    MadridFines._load(2024, 12, mock_cache)


class TestCleanFechaColumnDrop:
    """Cubre la eliminación de columna fecha redundante (línea 306)."""

    def test_fecha_columna_se_elimina_tras_set_index(self):
        """Cuando el CSV incluye una columna llamada 'fecha', _clean la elimina."""
        csv = (
            "CALIFICACION;LUGAR;MES;ANIO;HORA;IMP_BOL;DESCUENTO;PUNTOS;"
            "DENUNCIANTE;HECHO-BOL;VEL_LIMITE;VEL_CIRCULA;COORDENADA-X;COORDENADA-Y;fecha\n"
            "LEVE;CL A;12;2024;10.0;60.0;SI;0;SER;EST;;;;;\n"
        )
        df = pd.read_csv(io.StringIO(csv), sep=";", encoding="latin1")
        assert "fecha" in df.columns   # columna existe antes de clean
        MadridFines._clean(df)
        assert "fecha" not in df.columns   # eliminada tras set_index
        assert df.index.name == "fecha"    # pero sigue siendo el índice


class TestClean100Coverage:
    """Cubre las 2 líneas restantes para llegar al 100%."""

    def test_hora_none_devuelve_cero(self):
        """HORA=None (NaN en pandas) dispara el except de ValueError/TypeError."""
        import numpy as np
        csv = (
            "CALIFICACION;LUGAR;MES;ANIO;HORA;IMP_BOL;DESCUENTO;PUNTOS;DENUNCIANTE;HECHO-BOL;VEL_LIMITE;VEL_CIRCULA;COORDENADA-X;COORDENADA-Y\n"
            "LEVE;CL A;12;2024;;60.0;SI;0;SER;EST;;;;\n"  # HORA vacía -> NaN
        )
        df = pd.read_csv(io.StringIO(csv), sep=";", encoding="latin1")
        # Forzar que HORA sea None para activar el TypeError en float(None)
        df["HORA"] = None
        MadridFines._clean(df)
        # El índice debe haberse creado sin error
        assert df.index.name == "fecha"

    def test_set_index_crea_columna_fecha_duplicada(self):
        """Fuerza la rama 'if fecha in df.columns' tras set_index."""
        csv = (
            "CALIFICACION;LUGAR;MES;ANIO;HORA;IMP_BOL;DESCUENTO;PUNTOS;DENUNCIANTE;HECHO-BOL;VEL_LIMITE;VEL_CIRCULA;COORDENADA-X;COORDENADA-Y\n"
            "LEVE;CL A;12;2024;10.0;60.0;SI;0;SER;EST;;;;\n"
        )
        df = pd.read_csv(io.StringIO(csv), sep=";", encoding="latin1")
        # Creamos columna 'fecha' antes de llamar _clean
        # para que exista TANTO como columna como índice tras set_index
        df.insert(0, "fecha", pd.Timestamp("2024-12-01 10:00"))
        MadridFines._clean(df)
        assert df.index.name == "fecha"
        assert "fecha" not in df.columns


class TestLoadDirect:
    """Cubre la línea 'return df' en _load llamando directamente al método."""

    def test_load_directo_exitoso(self, test_cache_dir):
        """Llama _load directamente (sin mock de _load) para cubrir return df."""
        mock_cache = MagicMock()
        mock_cache.get.return_value = SAMPLE_CSV_DEC24

        with patch("traficFines.madridFines.get_url",
                   return_value="https://fake.url/202412.csv"):
            df = MadridFines._load(2024, 12, mock_cache)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5

    def test_clean_drop_fecha_column_real(self):
        """Fuerza que pandas deje 'fecha' como columna Y como índice."""
        csv = (
            "fecha;CALIFICACION;LUGAR;MES;ANIO;HORA;IMP_BOL;DESCUENTO;PUNTOS;"
            "DENUNCIANTE;HECHO-BOL;VEL_LIMITE;VEL_CIRCULA;COORDENADA-X;COORDENADA-Y\n"
            "2024-12-01;LEVE;CL A;12;2024;10.0;60.0;SI;0;SER;EST;;;;\n"
        )
        df = pd.read_csv(io.StringIO(csv), sep=";", encoding="latin1")
        # df ya tiene columna 'fecha'; _clean también calculará una nueva 'fecha'
        # y set_index la usará -> la columna original puede quedar
        MadridFines._clean(df)
        assert df.index.name == "fecha"
        assert "fecha" not in df.columns
