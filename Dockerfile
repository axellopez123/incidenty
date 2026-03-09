FROM python:3.12-slim

WORKDIR /app

# Crea un entorno virtual en /opt/venv
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# COPIA PRIMERO LOS REQUISITOS
COPY requirements.txt .

# Instala dependencias primero (aprovecha cache de Docker)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Luego copia el resto del código
COPY . .

# Asegura que 'app' sea un paquete Python
RUN touch /app/app/__init__.py

# Define PYTHONPATH para importaciones correctas
ENV PYTHONPATH="/app"

EXPOSE 8009

# Copia y da permisos al script de entrada
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Ejecuta FastAPI
CMD ["/app/entrypoint.sh"]
