#!/bin/sh

set -e

echo "Esperando a PostgreSQL..."

# Esperar a que PostgreSQL esté disponible
#while ! python -c "
#import socket
#import sys
#s = socket.socket()
#try:
#    s.connect(('db', 5432))
#    s.close()
#except Exception:
#    sys.exit(1)
#"
#do
#  echo "PostgreSQL no disponible aún..."
#  sleep 2
#done

#echo "PostgreSQL listo."

echo "Aplicando migraciones Alembic..."

alembic upgrade head

echo "Migraciones aplicadas."

echo "Iniciando FastAPI..."

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8008 \
    --workers 1 \
    --reload