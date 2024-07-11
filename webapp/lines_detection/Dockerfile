# Utiliza una imagen base de Python
FROM python:3.11.9

# Establece el directorio de trabajo
WORKDIR .
# Copia el script al contenedor
COPY lines_detection.py .

# Instala las dependencias necesarias
RUN pip install -r requirements.txt

# Comando para ejecutar el script
CMD ["python", "lines_detection.py"]