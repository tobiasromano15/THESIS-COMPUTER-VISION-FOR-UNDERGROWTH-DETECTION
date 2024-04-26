import cv2


class Decolor:
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt
    def getImage(self,path):
        # Cargar la imagen original
        image_path = 'DJI_0589.JPG'
        original_image = cv2.imread(image_path)

        # Convertir la imagen de RGB a HSV
        hsv_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

        # Definir el rango de color verde en HSV
        # Estos valores pueden necesitar ajustes
        lower_green = np.array([25, 52, 72])
        upper_green = np.array([102, 255, 255])

        # Crear una máscara que identifique los verdes
        mask = cv2.inRange(hsv_image, lower_green, upper_green)

        # Invertir la máscara para que los verdes sean negros y el resto blanco
        mask_inv = cv2.bitwise_not(mask)

        # Guardar la imagen de la máscara invertida
        label_image_path = 'DJI_0380_label_green.png'
        cv2.imwrite(label_image_path, mask_inv)

        # Mostrar la imagen original y la imagen de la máscara invertida
        fig, ax = plt.subplots(1, 2, figsize=(12, 6))

        # Mostrar imagen original
        ax[0].imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
        ax[0].set_title('Original Image')
        ax[0].axis('off')

        # Mostrar imagen de la máscara invertida
        ax[1].imshow(mask_inv, cmap='gray')
        ax[1].set_title('Mask Inverted (Green to Black)')
        ax[1].axis('off')

        plt.show()
        return mask_inv