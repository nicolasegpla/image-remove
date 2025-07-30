# Imagen base ligera con Python 3.10
FROM python:3.10-slim

# Evita prompts durante apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Directorio de trabajo
WORKDIR /app

# Copia requirements y los instala
COPY requirements.txt .

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        wget \
        ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente
COPY . .

# Descarga previa del modelo isnet-general-use para evitar descarga en caliente (opcional)
RUN mkdir -p /root/.u2net
   # wget -O /root/.u2net/isnet-general-use.onnx \
   #https://huggingface.co/DaDetIsnet/real-isnet/resolve/main/isnet-general-use.onnx

# Exponer el puerto por defecto de uvicorn
EXPOSE 8000

# Comando por defecto (puedes ajustar si usas gunicorn/uvicorn con workers)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]