import cv2
import numpy as np

# Cargar la imagen
ruta_imagen = 'subimagenes/subimage_0_0.png'
imagen = cv2.imread(ruta_imagen)

# Convertir la imagen de BGR a HSV
imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

# Definir el rango de color para los verdes (en HSV)
lower_green = np.array([35, 25, 25])  # Ajustado para incluir verdes más oscuros
upper_green = np.array([85, 255, 255])

# Crear la máscara para los píxeles verdes
mascara_verde = cv2.inRange(imagen_hsv, lower_green, upper_green)

# Definir el rango de color para rojos muy fuertes (en HSV)
lower_red1 = np.array([0, 150, 150])  # Rojos fuertes
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 150, 150])
upper_red2 = np.array([180, 255, 255])

# Crear la máscara para los píxeles rojos muy fuertes
mascara_rojo1 = cv2.inRange(imagen_hsv, lower_red1, upper_red1)
mascara_rojo2 = cv2.inRange(imagen_hsv, lower_red2, upper_red2)
mascara_rojo = cv2.bitwise_or(mascara_rojo1, mascara_rojo2)

# Expandir la máscara roja para incluir áreas adyacentes
kernel = np.ones((3, 3), np.uint8)
mascara_roja_dilatada = cv2.dilate(mascara_rojo, kernel, iterations=2)

# Encontrar los píxeles verdes adyacentes a la línea roja dilatada
mascara_interseccion = cv2.bitwise_and(mascara_verde, mascara_roja_dilatada)

# Inicializar la máscara final de píxeles verdes que deben eliminarse
mascara_final_eliminar = mascara_interseccion.copy()

# Eliminación en cadena con límite de iteraciones
max_iteraciones = 5000
iteraciones = 0
cambio = True

while cambio and iteraciones < max_iteraciones:
    iteraciones += 1
    # Encontrar los píxeles verdes adyacentes a los ya eliminados
    mascara_dilatada = cv2.dilate(mascara_final_eliminar, kernel, iterations=1)
    nuevos_puntos_a_eliminar = cv2.bitwise_and(mascara_verde, mascara_dilatada)

    # Verificar si hay nuevos píxeles para eliminar
    if cv2.countNonZero(nuevos_puntos_a_eliminar) == 0:
        cambio = False
    else:
        # Agregar los nuevos puntos a la máscara final de eliminación
        mascara_final_eliminar = cv2.bitwise_or(mascara_final_eliminar, nuevos_puntos_a_eliminar)

# Invertir la máscara final para borrar los píxeles verdes adyacentes a la línea roja
mascara_invertida = cv2.bitwise_not(mascara_final_eliminar)

# Aplicar la máscara invertida a la imagen original para eliminar los píxeles verdes adyacentes
imagen_sin_verdes_adyacentes = cv2.bitwise_and(imagen, imagen, mask=mascara_invertida)

# Sobrescribir la imagen original
cv2.imwrite(ruta_imagen, imagen_sin_verdes_adyacentes)
