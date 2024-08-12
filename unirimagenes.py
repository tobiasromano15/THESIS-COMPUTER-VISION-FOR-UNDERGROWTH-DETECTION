import cv2
import numpy as np
import os

def unir_subimagenes(subimage_folder, num_divisiones_x, num_divisiones_y, output_image_path):
    # Lista para almacenar filas de subimágenes
    filas_de_subimagenes = []

    for i in range(num_divisiones_y):
        # Lista para almacenar una fila de subimágenes
        fila = []
        for j in range(num_divisiones_x):
            # Leer la subimagen
            subimage_path = os.path.join(subimage_folder, f'subimage_{i}_{j}.png')
            subimage = cv2.imread(subimage_path)
            if subimage is None:
                raise ValueError(f"No se pudo cargar la subimagen en la ruta: {subimage_path}")
            fila.append(subimage)
        # Unir las subimágenes en la dimensión horizontal
        fila_unida = np.hstack(fila)
        filas_de_subimagenes.append(fila_unida)

    # Unir las filas en la dimensión vertical
    imagen_unida = np.vstack(filas_de_subimagenes)

    # Guardar la imagen unida
    cv2.imwrite(output_image_path, imagen_unida)

    return imagen_unida

# Ejemplo de uso
subimage_folder = 'subimagenes/'
output_image_path = 'C:/Users/Tobi/Desktop/TESIS/TESIS/subimagenes/imagen_unida.jpg'
num_divisiones_x = 4
num_divisiones_y = 2

imagen_unida = unir_subimagenes(subimage_folder, num_divisiones_x, num_divisiones_y, output_image_path)
