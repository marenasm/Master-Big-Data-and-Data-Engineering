"""
Módulo madridFines
==================
Proporciona la función ``get_url`` y la clase ``MadridFines`` para descargar,
limpiar y analizar datos de multas de tráfico del Ayuntamiento de Madrid
publicados en el portal de datos abiertos.

Portal: https://datos.madrid.es

Constantes
----------
RAIZ             : URL base del portal.
MADRID_FINES_URL : Ruta relativa a la página de multas de circulación.

Clases
------
- MadridError  : Excepción base del módulo.
- MadridFines  : Gestión completa del ciclo de análisis de multas.

Funciones
---------
- get_url(year, month): Devuelve la URL del CSV para un mes y año dados.
"""

import io
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .cache import CacheUrl, CacheError

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

RAIZ = "https://datos.madrid.es"
MADRID_FINES_URL = "dataset/210104-0-multas-circulacion-detalle/downloads"

_FULL_URL = RAIZ + "/" + MADRID_FINES_URL

# Nombres de columnas de coordenadas con guion y con guión bajo
_COORD_VARIANTS = {
    "COORDENADA-X": "COORDENADA_X",
    "COORDENADA-Y": "COORDENADA_Y",
}

# Columnas de texto que deben limpiarse de espacios
_TEXT_COLUMNS = ["CALIFICACION", "DESCUENTO", "HECHO-BOL", "DENUNCIANTE",
                 "LUGAR", "HECHO_BOL"]

# Columnas numéricas
_NUMERIC_COLUMNS = ["VEL_LIMITE", "VEL_CIRCULA", "COORDENADA_X", "COORDENADA_Y"]

# Meses en español para parsear los enlaces del portal
_MONTH_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}


def _hora_to_time(hora) -> tuple[int, int]:
    """Convierte hora decimal (ej. 20.23) a horas y minutos enteros.

    Parameters
    ----------
    hora :
        Valor de hora en formato decimal (ej. 20.23 → 20h 23min).

    Returns
    -------
    tuple[int, int]
        Par ``(hora, minuto)`` como enteros. Devuelve ``(0, 0)`` si el
        valor no es convertible.
    """
    try:
        h = float(hora)
        hora_int = int(h)
        minuto_int = round((h - hora_int) * 100)  # .23 → 23 minutos
        if not (0 <= minuto_int <= 59):
            minuto_int = 0
        return hora_int, minuto_int
    except (ValueError, TypeError):
        return 0, 0


# ---------------------------------------------------------------------------
# Excepción
# ---------------------------------------------------------------------------

class MadridError(Exception):
    """Excepción lanzada ante cualquier error en el módulo madridFines."""


# ---------------------------------------------------------------------------
# Función get_url
# ---------------------------------------------------------------------------

def get_url(year: int, month: int) -> str:
    """Devuelve la URL del fichero CSV de multas para *year* y *month*.

    Realiza scraping sobre el portal de datos abiertos del Ayuntamiento de
    Madrid para localizar el enlace exacto al CSV del mes solicitado.

    Parameters
    ----------
    year : int
        Año con cuatro dígitos (ej. 2024).  Solo se aceptan años >= 2017.
    month : int
        Mes (1–12).

    Returns
    -------
    str
        URL absoluta al fichero CSV.

    Raises
    ------
    MadridError
        Si el mes/año no se encuentra en la página o si ocurre un error de
        red.
    """
    if not (1 <= month <= 12):
        raise MadridError(f"Mes no válido: {month}. Debe estar entre 1 y 12.")
    if year < 2017:
        raise MadridError(f"Año {year} anterior a 2017; sin datos disponibles.")

    try:
        response = requests.get(_FULL_URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise MadridError(f"Error al acceder al portal de Madrid: {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")

    # La página de descargas lista cada recurso en un bloque <div class="row g-0">.
    # Cada bloque "Detalle" contiene el nombre del mes y año en su texto y un
    # enlace de descarga directa al CSV.  Los bloques "Agrupadas" se ignoran.
    # El portal usa dos órdenes según la antigüedad del recurso:
    #   Reciente  → "Detalle. Diciembre 2024"   (mes primero)
    #   Histórico → "... 2024 Enero. Detalle"   (año primero)
    # Por eso se comprueba que el mes Y el año estén presentes, en cualquier orden.
    month_name = [k for k, v in _MONTH_ES.items() if v == month][0]

    for div in soup.find_all("div", class_=lambda c: c and "row" in c and "g-0" in c):
        text = div.get_text(strip=True).lower()
        if "detalle" not in text or "agrupadas" in text:
            continue
        if month_name not in text or str(year) not in text:
            continue
        link = div.find("a", href=lambda h: h and "/download/" in h)
        if link:
            href: str = link["href"]
            if not href.startswith("http"):
                href = RAIZ + "/" + href.lstrip("/")
            return href

    raise MadridError(
        f"No se encontró la URL para {month:02d}/{year} en el portal de Madrid."
    )


# ---------------------------------------------------------------------------
# Clase MadridFines
# ---------------------------------------------------------------------------

class MadridFines:
    """Gestiona la descarga, limpieza y análisis de multas de Madrid.

    Automatiza el ciclo completo: descarga mediante caché, preprocesamiento
    y análisis estadístico de los datos de multas de tráfico.

    Parameters
    ----------
    app_name : str, optional
        Nombre de la aplicación para la caché.  Por defecto
        ``"madrid_fines"``.
    obsolescence : int, optional
        Días de validez de los ficheros en caché.  Por defecto 7.

    Attributes
    ----------
    cacheurl : CacheUrl
        Objeto que gestiona la caché de descargas.
    """

    def __init__(
        self,
        app_name: str = "madrid_fines",
        obsolescence: int = 7,
    ) -> None:
        self.cacheurl = CacheUrl(app_name=app_name, obsolescence=obsolescence)
        self._data: pd.DataFrame = pd.DataFrame()
        self._loaded: list[tuple[int, int]] = []

    # ------------------------------------------------------------------
    # Propiedades de solo lectura
    # ------------------------------------------------------------------

    @property
    def data(self) -> pd.DataFrame:
        """DataFrame con todas las multas cargadas (solo lectura)."""
        return self._data

    @property
    def loaded(self) -> list[tuple[int, int]]:
        """Lista de tuplas ``(month, year)`` de los meses cargados."""
        return list(self._loaded)

    # ------------------------------------------------------------------
    # Métodos internos estáticos
    # ------------------------------------------------------------------

    @staticmethod
    def _load(year: int, month: int, cacheurl: CacheUrl) -> pd.DataFrame:
        """Descarga (o recupera de caché) el CSV de multas y lo devuelve.

        Parameters
        ----------
        year : int
            Año de los datos.
        month : int
            Mes de los datos.
        cacheurl : CacheUrl
            Objeto de caché para gestionar la descarga.

        Returns
        -------
        pd.DataFrame
            Datos crudos del CSV.

        Raises
        ------
        MadridError
            Si no se puede obtener la URL o descargar los datos.
        """
        try:
            url = get_url(year, month)
        except MadridError:
            raise
        try:
            content = cacheurl.get(url)
        except CacheError as exc:
            raise MadridError(f"Error al descargar datos: {exc}") from exc

        try:
            df = pd.read_csv(
                io.StringIO(content),
                sep=";",
                encoding="latin1",
                low_memory=False,
            )
        except Exception as exc:
            raise MadridError(f"Error al parsear el CSV: {exc}") from exc
        return df

    @staticmethod
    def _clean(df: pd.DataFrame) -> None:
        """Limpia y normaliza el DataFrame *df* en el sitio (*in-place*).

        Operaciones realizadas:

        1. Elimina espacios en los nombres de las columnas.
        2. Normaliza variantes de nombres de coordenadas
           (``COORDENADA-X`` → ``COORDENADA_X``).
        3. Elimina espacios en columnas de texto.
        4. Convierte columnas de velocidad y coordenadas a numérico.
        5. Crea la columna ``fecha`` (datetime) a partir de ``ANIO``,
           ``MES`` y ``HORA``, y la establece como índice.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame a limpiar (se modifica en el sitio).
        """
        # 1. Limpiar nombres de columnas
        df.columns = df.columns.str.strip()

        # 2. Renombrar variantes de coordenadas (guion → guión bajo)
        rename_map = {}
        for old, new in _COORD_VARIANTS.items():
            if old in df.columns:
                rename_map[old] = new
        if rename_map:
            df.rename(columns=rename_map, inplace=True)

        # También renombrar HECHO-BOL → HECHO_BOL si existe
        if "HECHO-BOL" in df.columns:
            df.rename(columns={"HECHO-BOL": "HECHO_BOL"}, inplace=True)

        # 3. Limpiar espacios en columnas de texto
        for col in _TEXT_COLUMNS:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # 4. Convertir columnas numéricas
        numeric_cols = [c for c in _NUMERIC_COLUMNS if c in df.columns]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 5. Crear columna fecha y establecerla como índice
        if {"ANIO", "MES", "HORA"}.issubset(df.columns):
            hm = df["HORA"].apply(_hora_to_time)
            hora_entera = hm.apply(lambda x: x[0])
            minuto_entero = hm.apply(lambda x: x[1])
            df["fecha"] = pd.to_datetime(
                {
                    "year": df["ANIO"],
                    "month": df["MES"],
                    "day": 1,
                    "hour": hora_entera,
                    "minute": minuto_entero,
                },
                errors="coerce",
            )
            df.set_index("fecha", inplace=True)
            # Eliminar columna fecha redundante si quedó
            if "fecha" in df.columns:
                df.drop(columns=["fecha"], inplace=True)  # pragma: no cover

    # ------------------------------------------------------------------
    # Métodos públicos
    # ------------------------------------------------------------------

    def add(self, year: int, month: Optional[int] = None) -> None:
        """Añade datos de multas de un mes (o año completo) al dataset.

        Si el mes ya está cargado, no hace nada.  Si ``month`` es ``None``,
        se intentan cargar todos los meses del año.

        Parameters
        ----------
        year : int
            Año de los datos.
        month : int | None, optional
            Mes (1–12).  Si es ``None`` se carga el año completo.

        Raises
        ------
        MadridError
            Si no se pueden obtener o parsear los datos.
        """
        if month is None:
            for m in range(1, 13):
                try:
                    self.add(year, m)
                except MadridError:
                    pass  # Mes no disponible; continuar con el siguiente
            return

        if (month, year) in self._loaded:
            return  # Ya cargado

        df = self._load(year, month, self.cacheurl)
        self._clean(df)

        if self._data.empty:
            self._data = df
        else:
            self._data = pd.concat([self._data, df])

        self._loaded.append((month, year))

    def fines_hour(self, fig_name: str) -> None:
        """Genera y guarda un gráfico de multas por hora del día.

        Dibuja una línea por cada mes/año cargado mostrando la distribución
        de multas a lo largo de las 24 horas.

        Parameters
        ----------
        fig_name : str
            Ruta/nombre del fichero de imagen a generar (ej.
            ``"evolucion_multas.png"``).

        Raises
        ------
        MadridError
            Si no hay datos cargados.
        """
        if self._data.empty:
            raise MadridError("No hay datos cargados. Usa add() primero.")

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(12, 6))

        for (month, year) in sorted(self._loaded):
            mask = (self._data["MES"] == month) & (self._data["ANIO"] == year)
            subset = self._data[mask]
            if subset.empty:
                continue
            # Agrupar por hora (extraída del índice)
            counts = subset.groupby(subset.index.hour).size()
            ax.plot(counts.index, counts.values, marker="o",
                    label=f"{month:02d}/{year}")

        ax.set_title("Evolución de multas por hora del día")
        ax.set_xlabel("Hora del día")
        ax.set_ylabel("Número de multas")
        ax.set_xticks(range(0, 24))
        ax.legend(title="Mes/Año")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(fig_name, dpi=150)
        plt.close(fig)

    def fines_calification(self) -> pd.DataFrame:
        """Distribución de multas por calificación, mes y año.

        Returns
        -------
        pd.DataFrame
            Tabla pivote con columnas ``GRAVE``, ``LEVE``, ``MUY GRAVE``
            e índice múltiple ``(MES, ANIO)``.

        Raises
        ------
        MadridError
            Si no hay datos cargados.
        """
        if self._data.empty:
            raise MadridError("No hay datos cargados. Usa add() primero.")

        df = self._data.reset_index()
        result = (
            df.groupby(["MES", "ANIO", "CALIFICACION"])
            .size()
            .unstack(fill_value=0)
        )
        result.index.names = ["MES", "ANIO"]
        return result

    def total_payment(self) -> pd.DataFrame:
        """Resumen de importes de multas por mes y año.

        Calcula el importe máximo (sin descuento) y mínimo (con descuento
        del 50 %) recaudado, agrupando por mes y año.

        Returns
        -------
        pd.DataFrame
            DataFrame con columnas ``importe_maximo`` e
            ``importe_minimo`` e índice múltiple ``(MES, ANIO)``.

        Raises
        ------
        MadridError
            Si no hay datos cargados o falta la columna ``IMP_BOL``.
        """
        if self._data.empty:
            raise MadridError("No hay datos cargados. Usa add() primero.")
        if "IMP_BOL" not in self._data.columns:
            raise MadridError("La columna IMP_BOL no está disponible.")

        df = self._data.reset_index()
        grouped = df.groupby(["MES", "ANIO"])["IMP_BOL"]
        summary = pd.DataFrame(
            {
                "importe_maximo": grouped.sum(),          # todos pagan sin dto.
                "importe_minimo": grouped.sum() * 0.5,    # todos acogen dto. 50%
            }
        )
        summary.index.names = ["MES", "ANIO"]
        return summary

    def __repr__(self) -> str:  # pragma: no cover
        meses = [(f"{m:02d}/{y}") for m, y in self._loaded]
        return (
            f"MadridFines(meses_cargados={meses}, "
            f"total_filas={len(self._data)})"
        )
