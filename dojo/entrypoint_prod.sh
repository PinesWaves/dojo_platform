#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

if [ "$DATABASE" = "postgres" ]; then
    echo "Esperando a que PostgreSQL esté disponible..."

    while ! nc -z "${DOJO_DB_HOST}" "${DOJO_DB_PORT}"; do
      sleep 0.1
    done

    echo "PostgreSQL iniciado"
fi

# Crear y aplicar migraciones de Django
python manage.py makemigrations
python manage.py migrate --noinput

# Recoger archivos estáticos
python manage.py collectstatic --noinput

# Iniciar Gunicorn en modo producción
exec gunicorn myproject.wsgi:application --bind 0.0.0.0:8000 --workers 3
