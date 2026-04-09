@echo off
REM setup.bat — Instala el paquete traficFines en Windows
REM Uso: doble clic o ejecutar desde cmd

echo === Creando entorno virtual (.venv) ===
python -m venv .venv

echo === Activando entorno virtual ===
call .venv\Scripts\activate.bat

echo === Actualizando pip ===
pip install --upgrade pip

echo === Instalando dependencias ===
pip install -r requirements.txt

echo === Instalando el paquete en modo editable ===
pip install -e .

echo.
echo Instalacion completada.
echo Para activar el entorno: .venv\Scripts\activate.bat
pause