# Etapa 1: Base para dependencias
FROM python:3.10-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Etapa 2: Instalación de dependencias y ejecución de Tests
FROM base AS builder
COPY requirements/ requirements/
# Instalamos dependencias de test para validar el código
RUN pip install --no-cache-dir -r requirements/tests.txt

COPY . .
# Ejecución de tests (opcional: se puede comentar si se prefiere manejar en el CI)
# RUN pytest

# Etapa 3: Imagen final de Producción
FROM base AS runtime
# Copiamos solo las dependencias instaladas (opcionalmente puedes reinstalar solo runtime)
COPY requirements/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos solo el código fuente necesario
COPY ./src ./src
COPY .env.example ./.env 

# Exponer el puerto de FastAPI
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]