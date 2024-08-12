# Utiliza una imagen base de Python
FROM python:3.11.9

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instala las dependencias necesarias
RUN pip install -r requirements.txt

# Copia el resto de los archivos al contenedor
COPY lines_detection.py .

# Comando para ejecutar el script
CMD ["python", "lines_detection.py"]
