"""
traficFines
===========
Paquete para la descarga, limpieza y análisis de datos de multas de tráfico
del Ayuntamiento de Madrid (portal datos.madrid.es).

Módulos
-------
cache        : Clases ``Cache`` y ``CacheUrl`` para caché local.
madridFines  : Clase ``MadridFines`` y función ``get_url``.

Uso rápido
----------
>>> from traficFines import MadridFines
>>> mf = MadridFines()
>>> mf.add(2024, 12)
>>> print(mf.data.shape)
>>> mf.fines_hour("multas_hora.png")
"""

from .cache import Cache, CacheUrl, CacheError
from .madridFines import MadridFines, MadridError, get_url

__all__ = [
    "Cache",
    "CacheUrl",
    "CacheError",
    "MadridFines",
    "MadridError",
    "get_url",
]

