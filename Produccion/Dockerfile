
# Imagen base de Python
FROM python:3.13-slim

# Configuración de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalación de dependencias
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia del código del proyecto
COPY . .

# Puerto utilizado por Django
EXPOSE 8000
