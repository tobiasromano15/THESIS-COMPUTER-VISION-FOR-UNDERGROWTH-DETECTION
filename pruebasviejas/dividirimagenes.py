import cv2
import numpy as np
import os
import shutil

def remove_directory_if_not_empty(directory):
    if os.path.exists(directory) and os.path.isdir(directory):
        if os.listdir(directory):
            shutil.rmtree(directory)



def dividir_y_guardar_subimagenes(image_path, num_divisiones_x, num_divisiones_y, output_path):
    remove_directory_if_not_empty(output_path)
    # Leer la imagen original
    image = cv2.imread(image_path)

    # Obtener las dimensiones de la imagen
    height, width, _ = image.shape

    # Calcular las dimensiones de las subimágenes
    subimage_width = width // num_divisiones_x
    subimage_height = height // num_divisiones_y

    # Crear el directorio de salida si no existe
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Extraer y guardar las subimágenes
    for i in range(num_divisiones_y):
        for j in range(num_divisiones_x):
            # Calcular las coordenadas de la subimagen
            x_start = j * subimage_width
            y_start = i * subimage_height
            x_end = x_start + subimage_width
            y_end = y_start + subimage_height

            # Extraer la subimagen
            subimage = image[y_start:y_end, x_start:x_end]

            # Guardar la subimagen
            cv2.imwrite(f'{output_path}/subimage_{i}_{j}.png', subimage)



"""# Ejemplo de uso
image_path = 'lejos2.jpg'
print(image_path)
output_path = 'C:/Users/Tobi/Desktop/TESIS/TESIS/subimagenes'
num_divisiones_x = 4
num_divisiones_y = 2
dividir_y_guardar_subimagenes(image_path, num_divisiones_x, num_divisiones_y, output_path)
"""
