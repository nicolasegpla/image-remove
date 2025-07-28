# Usamos una imagen base ligera con Python
FROM python:3.10-slim

# Evita prompts interactivos en la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Creamos y usamos un directorio de trabajo
WORKDIR /app

# Copiamos requirements y los instalamos
COPY requirements.txt .

# Instalación del sistema y dependencias necesarias
RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del proyecto
COPY . .

# Exponer el puerto por defecto de uvicorn
EXPOSE 8000

# Comando para ejecutar FastAPI con autoreload desactivado (modo producción)
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]