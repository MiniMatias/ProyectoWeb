#!/usr/bin/env bash
# Exit on error
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos (Bootstrap, CSS)
python manage.py collectstatic --no-input

# Aplicar migraciones a la base de datos de producción
python manage.py migrate