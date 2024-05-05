import numpy as np
import cv2
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt

# Cargar la imagen
img = cv2.imread('/mnt/data/FOTO1.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Cambiar el tamaño de la imagen para una rápida demostración
img = cv2.resize(img, (img.shape[1] // 4, img.shape[0] // 4))

# Preparar los datos para el clustering
data = img.reshape((-1, 3))

# Clustering K-means
kmeans = KMeans(n_clusters=2, random_state=0).fit(data)
segmented_img = kmeans.labels_.reshape(img.shape[:2])

# Visualizar los resultados
plt.figure(figsize=(10, 5))
plt.subplot(121)
plt.imshow(img)
plt.title('Original Image')
plt.subplot(122)
plt.imshow(segmented_img, cmap='gray')
plt.title('Segmented Image')
plt.show()
