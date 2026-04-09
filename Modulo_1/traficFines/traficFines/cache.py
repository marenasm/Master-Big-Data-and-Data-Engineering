"""
Módulo cache
============
Proporciona las clases ``Cache`` y ``CacheUrl`` para almacenar y recuperar
datos en disco, evitando descargas repetidas desde Internet.

Clases
------
- CacheError : Excepción base del módulo.
- Cache      : Gestión de ficheros en un directorio local.
- CacheUrl   : Especialización de Cache para URLs de Internet.
"""

import hashlib
import time
from pathlib import Path
import requests


# ---------------------------------------------------------------------------
# Excepción
# ---------------------------------------------------------------------------

class CacheError(Exception):
    """Excepción lanzada ante cualquier error en el módulo cache."""


# ---------------------------------------------------------------------------
# Clase Cache
# ---------------------------------------------------------------------------

_DEFAULT_CACHE_DIR = Path.home() / ".my_cache"
_DEFAULT_OBSOLESCENCE = 7  # días


class Cache:
    """Gestiona el almacenamiento de ficheros en un directorio local.

    Cada instancia trabaja dentro de una subcarpeta propia
    (``cache_dir / app_name``) para evitar colisiones entre aplicaciones.

    Parameters
    ----------
    app_name : str
        Nombre que identifica la aplicación. Se crea una subcarpeta con
        este nombre dentro de *base_dir*.
    base_dir : Path | str | None, optional
        Directorio raíz de la caché.  Por defecto ``~/.my_cache``.
    obsolescence : int, optional
        Número de días tras los cuales un fichero se considera obsoleto.
        Por defecto 7.

    Raises
    ------
    CacheError
        Si no se puede crear el directorio de caché.
    """

    def __init__(
        self,
        app_name: str,
        base_dir: "Path | str | None" = None,
        obsolescence: int = _DEFAULT_OBSOLESCENCE,
    ) -> None:
        if base_dir is None:
            base_dir = _DEFAULT_CACHE_DIR
        self._app_name: str = app_name
        self._cache_dir: Path = Path(base_dir) / app_name
        self._obsolescence: int = obsolescence
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise CacheError(
                f"No se pudo crear el directorio de caché '{self._cache_dir}': {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Propiedades de solo lectura
    # ------------------------------------------------------------------

    @property
    def app_name(self) -> str:
        """Nombre de la aplicación."""
        return self._app_name

    @property
    def cache_dir(self) -> Path:
        """Ruta completa del directorio de caché de la aplicación."""
        return self._cache_dir

    @property
    def obsolescence(self) -> int:
        """Días de validez de los ficheros en caché."""
        return self._obsolescence

    # ------------------------------------------------------------------
    # Métodos públicos
    # ------------------------------------------------------------------

    def _path(self, name: str) -> Path:
        """Devuelve la ruta absoluta del fichero con nombre *name*."""
        return self._cache_dir / name

    def set(self, name: str, data: str) -> None:
        """Almacena *data* en la caché con el identificador *name*.

        Parameters
        ----------
        name : str
            Identificador (nombre de fichero) bajo el que se guarda *data*.
        data : str
            Contenido a persistir.

        Raises
        ------
        CacheError
            Si ocurre un error de escritura.
        """
        path = self._path(name)
        try:
            path.write_text(data, encoding="utf-8")
        except OSError as exc:
            raise CacheError(f"Error al escribir en caché '{path}': {exc}") from exc

    def exists(self, name: str) -> bool:
        """Comprueba si existe un fichero con identificador *name*.

        Parameters
        ----------
        name : str
            Identificador a comprobar.

        Returns
        -------
        bool
            ``True`` si el fichero existe, ``False`` en caso contrario.
        """
        return self._path(name).is_file()

    def load(self, name: str) -> str:
        """Recupera el contenido almacenado bajo el identificador *name*.

        Parameters
        ----------
        name : str
            Identificador del fichero a recuperar.

        Returns
        -------
        str
            Contenido del fichero.

        Raises
        ------
        CacheError
            Si el fichero no existe o no puede leerse.
        """
        path = self._path(name)
        if not path.is_file():
            raise CacheError(f"El elemento '{name}' no existe en la caché.")
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise CacheError(f"Error al leer de caché '{path}': {exc}") from exc

    def how_old(self, name: str) -> float:
        """Devuelve la antigüedad en **milisegundos** del fichero *name*.

        Parameters
        ----------
        name : str
            Identificador del fichero.

        Returns
        -------
        float
            Milisegundos transcurridos desde la última modificación.

        Raises
        ------
        CacheError
            Si el fichero no existe.
        """
        path = self._path(name)
        if not path.is_file():
            raise CacheError(f"El elemento '{name}' no existe en la caché.")
        age_seconds = time.time() - path.stat().st_mtime
        return age_seconds * 1000.0

    def is_obsolete(self, name: str) -> bool:
        """Indica si el fichero *name* ha superado el período de validez.

        Trabaja siempre con el nombre de fichero en disco (sin hashear),
        usando ``_path()`` directamente para evitar problemas de polimorfismo
        cuando es llamado desde subclases que sobrescriben ``exists``/``how_old``.

        Parameters
        ----------
        name : str
            Identificador del fichero (nombre en disco, ya hasheado si procede).

        Returns
        -------
        bool
            ``True`` si el fichero es obsoleto o no existe.
        """
        path = self._path(name)
        if not path.is_file():
            return True
        age_seconds = time.time() - path.stat().st_mtime
        age_days = age_seconds / 86400
        return age_days > self._obsolescence

    def delete(self, name: str) -> None:
        """Elimina el fichero *name* de la caché.

        Si no existe, no se lanza ninguna excepción.

        Parameters
        ----------
        name : str
            Identificador del fichero a eliminar.
        """
        path = self._path(name)
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            raise CacheError(f"Error al eliminar '{path}': {exc}") from exc

    def clear(self) -> None:
        """Elimina todos los ficheros del directorio de caché.

        Raises
        ------
        CacheError
            Si ocurre un error durante el borrado.
        """
        try:
            for item in self._cache_dir.iterdir():
                if item.is_file():
                    item.unlink()
        except OSError as exc:
            raise CacheError(f"Error al limpiar la caché: {exc}") from exc

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Cache(app_name={self._app_name!r}, "
            f"cache_dir={self._cache_dir!r}, "
            f"obsolescence={self._obsolescence})"
        )


# ---------------------------------------------------------------------------
# Clase CacheUrl
# ---------------------------------------------------------------------------

class CacheUrl(Cache):
    """Especialización de class:`Cache` para URLs de Internet.

    Las URLs se convierten a un hash MD5 antes de usarlas como nombre de
    fichero, evitando caracteres no válidos en el sistema de ficheros.

    Parameters
    ----------
    app_name : str
        Nombre que identifica la aplicación.
    base_dir : Path | str | None, optional

        Directorio raíz de la caché.
    obsolescence : int, optional
        Días de validez.  Por defecto 7.
    """

    # ------------------------------------------------------------------
    # Métodos auxiliares privados
    # ------------------------------------------------------------------

    @staticmethod
    def _hash(url: str) -> str:
        """Calcula el hash MD5 de *url*.

        Parameters
        ----------
        url : str
            URL a hashear.

        Returns
        -------
        str
            Cadena hexadecimal de 32 caracteres.
        """
        return hashlib.md5(url.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Métodos públicos (sobrescriben los de Cache)
    # ------------------------------------------------------------------

    def get(self, url: str) -> str:
        """Devuelve el contenido de *url*, usando la caché si está disponible.

        Si el fichero no existe en caché o está obsoleto se descarga de nuevo
        y se almacena.

        Parameters
        ----------
        url : str
            URL a descargar.

        Returns
        -------
        str
            Contenido de la respuesta HTTP.

        Raises
        ------
        CacheError
            Si la descarga falla o el servidor devuelve un código de error.
        """
        name = self._hash(url)
        if not self.is_obsolete(name):
            return super().load(name)
        # Descargar
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CacheError(f"Error al descargar '{url}': {exc}") from exc
        content = response.text
        super().set(name, content)
        return content

    def exists(self, url: str) -> bool:  # type: ignore[override]
        """Comprueba si la URL está en caché.

        Parameters
        ----------
        url : str
            URL a comprobar.

        Returns
        -------
        bool
        """
        return super().exists(self._hash(url))

    def load(self, url: str) -> str:  # type: ignore[override]
        """Carga el contenido en caché asociado a *url*.

        Parameters
        ----------
        url : str
            URL cuyo contenido se quiere recuperar.

        Returns
        -------
        str

        Raises
        ------
        CacheError
            Si la URL no está en caché.
        """
        return super().load(self._hash(url))

    def how_old(self, url: str) -> float:  # type: ignore[override]
        """Devuelve la antigüedad en milisegundos del contenido de *url*.

        Parameters
        ----------
        url : str

        Returns
        -------
        float

        Raises
        ------
        CacheError
            Si la URL no está en caché.
        """
        return super().how_old(self._hash(url))

    def delete(self, url: str) -> None:  # type: ignore[override]
        """Elimina de la caché el contenido asociado a *url*.

        Parameters
        ----------
        url : str
        """
        super().delete(self._hash(url))

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CacheUrl(app_name={self._app_name!r}, "
            f"cache_dir={self._cache_dir!r}, "
            f"obsolescence={self._obsolescence})"
        )
