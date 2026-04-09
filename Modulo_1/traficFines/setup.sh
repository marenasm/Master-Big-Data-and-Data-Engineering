#!/bin/bash
# setup.sh — Instala el paquete traficFines en Linux/Mac
# Uso: bash setup.sh

set -e

echo "=== Creando entorno virtual (.venv) ==="
python3 -m venv .venv

echo "=== Activando entorno virtual ==="
source .venv/bin/activate

echo "=== Actualizando pip ==="
pip install --upgrade pip

echo "=== Instalando dependencias ==="
pip install -r requirements.txt

echo "=== Instalando el paquete en modo editable ==="
pip install -e .

echo ""
echo "Instalacion completada."
echo "Para activar el entorno: source .venv/bin/activate"