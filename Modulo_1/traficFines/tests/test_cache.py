"""
test_cache.py
=============
Tests unitarios para las clases ``Cache`` y ``CacheUrl`` del módulo
``traficFines.cache``.

Los accesos a Internet se simulan con mocks (unittest.mock).
Todos los ficheros de caché se crean en directorios temporales (tmp_path)
proporcionados por pytest.
"""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests as req

from traficFines.cache import Cache, CacheUrl, CacheError


# ===========================================================================
# Tests de la clase Cache
# ===========================================================================

class TestCacheInit:
    """Tests del constructor de Cache."""

    def test_crear_cache_crea_directorio(self, test_cache_dir):
        cache = Cache("test_app", base_dir=test_cache_dir)
        assert cache.cache_dir.exists()

    def test_propiedades_solo_lectura(self, test_cache_dir):
        cache = Cache("mi_app", base_dir=test_cache_dir, obsolescence=3)
        assert cache.app_name == "mi_app"
        assert cache.obsolescence == 3
        assert "mi_app" in str(cache.cache_dir)

    def test_no_se_puede_modificar_app_name(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        with pytest.raises(AttributeError):
            cache.app_name = "otro"

    def test_no_se_puede_modificar_cache_dir(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        with pytest.raises(AttributeError):
            cache.cache_dir = Path("/tmp/otro")

    def test_no_se_puede_modificar_obsolescence(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        with pytest.raises(AttributeError):
            cache.obsolescence = 99

    def test_directorio_por_defecto(self, monkeypatch):
        """Cache sin base_dir usa ~/.my_cache/<app>."""
        fake_home = Path("/tmp/fake_home")
        monkeypatch.setattr(Path, "home", staticmethod(lambda: fake_home))
        with patch("pathlib.Path.mkdir"):
            cache = Cache("app_default")
        assert "app_default" in str(cache.cache_dir)


class TestCacheSetLoad:
    """Tests de set() y load()."""

    def test_set_y_load_basico(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        cache.set("clave1", "contenido de prueba")
        assert cache.load("clave1") == "contenido de prueba"

    def test_set_sobreescribe(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        cache.set("k", "v1")
        cache.set("k", "v2")
        assert cache.load("k") == "v2"

    def test_load_no_existe_lanza_cacheerror(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        with pytest.raises(CacheError):
            cache.load("inexistente")

    def test_set_unicode(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        texto = "Multa de estacionamiento áéíóú ñ"
        cache.set("unicode", texto)
        assert cache.load("unicode") == texto


class TestCacheExists:
    """Tests de exists()."""

    def test_exists_true(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        cache.set("x", "dato")
        assert cache.exists("x") is True

    def test_exists_false(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        assert cache.exists("no_existe") is False


class TestCacheHowOld:
    """Tests de how_old()."""

    def test_how_old_devuelve_float(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        cache.set("archivo", "datos")
        age = cache.how_old("archivo")
        assert isinstance(age, float)
        assert age >= 0

    def test_how_old_no_existe_lanza_error(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        with pytest.raises(CacheError):
            cache.how_old("no_existe")

    def test_fichero_reciente_no_obsoleto(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir, obsolescence=7)
        cache.set("reciente", "datos")
        assert cache.is_obsolete("reciente") is False

    def test_fichero_obsoleto_por_fecha(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir, obsolescence=1)
        cache.set("viejo", "datos")
        path = cache.cache_dir / "viejo"
        # Modificamos el mtime para simular un fichero de hace 2 días
        old_time = time.time() - (2 * 86400)
        import os
        os.utime(path, (old_time, old_time))
        assert cache.is_obsolete("viejo") is True

    def test_no_existe_es_obsoleto(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        assert cache.is_obsolete("nunca_guardado") is True


class TestCacheDelete:
    """Tests de delete() y clear()."""

    def test_delete_existente(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        cache.set("borrar", "dato")
        cache.delete("borrar")
        assert cache.exists("borrar") is False

    def test_delete_no_existente_no_lanza(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        cache.delete("no_existe")  # No debe lanzar excepción

    def test_clear_borra_todo(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        cache.set("a", "1")
        cache.set("b", "2")
        cache.set("c", "3")
        cache.clear()
        assert cache.exists("a") is False
        assert cache.exists("b") is False
        assert cache.exists("c") is False

    def test_clear_directorio_vacio_no_lanza(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        cache.clear()  # No debe lanzar excepción


# ===========================================================================
# Tests de la clase CacheUrl
# ===========================================================================

class TestCacheUrlHash:
    """Tests del hash interno de CacheUrl."""

    def test_misma_url_mismo_hash(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        url = "https://ejemplo.com/datos.csv"
        h1 = cache._hash(url)
        h2 = cache._hash(url)
        assert h1 == h2

    def test_distintas_urls_distinto_hash(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        h1 = cache._hash("https://a.com")
        h2 = cache._hash("https://b.com")
        assert h1 != h2

    def test_hash_longitud_32(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        h = cache._hash("https://cualquier.url")
        assert len(h) == 32


class TestCacheUrlGet:
    """Tests del método get() de CacheUrl."""

    def test_get_descarga_y_cachea(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        url = "https://fake.url/datos.csv"
        contenido = "col1;col2\nv1;v2"

        mock_resp = MagicMock()
        mock_resp.text = contenido
        mock_resp.raise_for_status = MagicMock()

        with patch("traficFines.cache.requests.get", return_value=mock_resp) as mock_get:
            resultado = cache.get(url)
            assert resultado == contenido
            mock_get.assert_called_once_with(url, timeout=30)

    def test_get_usa_cache_segunda_vez(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir, obsolescence=7)
        url = "https://fake.url/datos.csv"
        contenido = "datos de prueba"

        mock_resp = MagicMock()
        mock_resp.text = contenido
        mock_resp.raise_for_status = MagicMock()

        with patch("traficFines.cache.requests.get", return_value=mock_resp) as mock_get:
            cache.get(url)          # primera vez: descarga
            cache.get(url)          # segunda vez: debería usar caché
            assert mock_get.call_count == 1  # solo una descarga

    def test_get_error_http_lanza_cacheerror(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        url = "https://fake.url/error.csv"

        with patch(
            "traficFines.cache.requests.get",
            side_effect=req.RequestException("Error de red"),
        ):
            with pytest.raises(CacheError):
                cache.get(url)

    def test_get_status_error_lanza_cacheerror(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        url = "https://fake.url/notfound.csv"

        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = req.HTTPError("404")

        with patch("traficFines.cache.requests.get", return_value=mock_resp):
            with pytest.raises(CacheError):
                cache.get(url)


class TestCacheUrlMetodosHeredados:
    """Tests de los métodos heredados adaptados a URLs."""

    def _cachear(self, cache, url, contenido):
        mock_resp = MagicMock()
        mock_resp.text = contenido
        mock_resp.raise_for_status = MagicMock()
        with patch("traficFines.cache.requests.get", return_value=mock_resp):
            cache.get(url)

    def test_exists_true(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        url = "https://fake.url/a.csv"
        self._cachear(cache, url, "datos")
        assert cache.exists(url) is True

    def test_exists_false(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        assert cache.exists("https://no.existe") is False

    def test_load_url_en_cache(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        url = "https://fake.url/b.csv"
        self._cachear(cache, url, "contenido_b")
        assert cache.load(url) == "contenido_b"

    def test_load_url_no_en_cache(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        with pytest.raises(CacheError):
            cache.load("https://no.en.cache")

    def test_how_old_url(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        url = "https://fake.url/c.csv"
        self._cachear(cache, url, "datos c")
        age = cache.how_old(url)
        assert isinstance(age, float)
        assert age >= 0

    def test_delete_url(self, test_cache_dir):
        cache = CacheUrl("url_app", base_dir=test_cache_dir)
        url = "https://fake.url/d.csv"
        self._cachear(cache, url, "datos d")
        cache.delete(url)
        assert cache.exists(url) is False


# ===========================================================================
# Tests de cobertura de ramas de error OSError
# ===========================================================================

class TestCacheOSErrors:
    """Cubre los bloques except OSError del módulo cache."""

    def test_init_mkdir_falla_lanza_cacheerror(self, test_cache_dir):
        from unittest.mock import patch as p
        with p("pathlib.Path.mkdir", side_effect=OSError("permiso denegado")):
            with pytest.raises(CacheError, match="No se pudo crear"):
                Cache("app_err", base_dir=test_cache_dir)

    def test_set_write_falla_lanza_cacheerror(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        from unittest.mock import patch as p
        with p("pathlib.Path.write_text", side_effect=OSError("disco lleno")):
            with pytest.raises(CacheError, match="Error al escribir"):
                cache.set("k", "v")

    def test_load_read_falla_lanza_cacheerror(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        cache.set("k", "v")
        from unittest.mock import patch as p
        with p("pathlib.Path.read_text", side_effect=OSError("error lectura")):
            with pytest.raises(CacheError, match="Error al leer"):
                cache.load("k")

    def test_delete_unlink_falla_lanza_cacheerror(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        cache.set("k", "v")
        from unittest.mock import patch as p
        with p("pathlib.Path.unlink", side_effect=OSError("error borrado")):
            with pytest.raises(CacheError, match="Error al eliminar"):
                cache.delete("k")

    def test_clear_iterdir_falla_lanza_cacheerror(self, test_cache_dir):
        cache = Cache("app", base_dir=test_cache_dir)
        cache.set("k", "v")
        from unittest.mock import patch as p
        with p("pathlib.Path.iterdir", side_effect=OSError("error iterdir")):
            with pytest.raises(CacheError, match="Error al limpiar"):
                cache.clear()
