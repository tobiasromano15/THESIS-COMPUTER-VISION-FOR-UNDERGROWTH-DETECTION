# Import necessary modules
import os
import numpy as np
import math 
import matplotlib.pyplot as plt
from matplotlib import cm, gridspec

# Geospatial libraries
import rasterio
import fiona
import geopandas as gpd

# Machine learning libraries
from skimage import feature
from skimage.transform import hough_line, hough_line_peaks

# Load the raster image
imgRaster = rasterio.open('mosaico.tif')
im = imgRaster.read(1)

# Apply Canny edge detection
edges1 = feature.canny(im)
edges2 = feature.canny(im, sigma=3)

# Use the Canny edge detection result with sigma=3
selImage = edges2

# Classic straight-line Hough transform
# Set a precision of 2 degrees
precision = 2

tested_angles = np.linspace(-np.pi / 2, np.pi / 2, int(180 / precision), endpoint=False)
h, theta, d = hough_line(selImage, theta=tested_angles)

# Define representative length of interpreted lines in pixels
selDiag = selImage.shape[1]
progRange = range(selDiag)
totalLines = []
angleList = []
for _, angle, dist in zip(*hough_line_peaks(h, theta, d)):
    (x0, y0) = dist * np.array([np.cos(angle), np.sin(angle)])
    if angle in [np.pi/2, -np.pi/2]:
        cols = [prog for prog in progRange]
        rows = [y0 for prog in progRange]
    elif angle == 0:
        cols = [x0 for prog in progRange]
        rows = [prog for prog in progRange]
    else:
        c0 = y0 + x0 / np.tan(angle)
        cols = [prog for prog in progRange]
        rows = [col * np.tan(angle + np.pi/2) + c0 for col in cols]

    partialLine = []
    for col, row in zip(cols, rows):
        partialLine.append(imgRaster.xy(row, col))
    totalLines.append(partialLine)
    if math.degrees(angle + np.pi/2) > 90:
        angleList.append(360 - math.degrees(angle + np.pi/2))
    else:
        angleList.append(math.degrees(angle + np.pi/2))

# Define schema
schema = {
    'properties': {'angle': 'float:16'},
    'geometry': 'LineString'
}

# Ensure the output directory exists
output_dir = 'Shp'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Output shapefile
outShp = fiona.open('Shp/croprows.shp', mode='w', driver='ESRI Shapefile', schema=schema, crs=imgRaster.crs)
for index, line in enumerate(totalLines):
    feature = {
        'geometry': {'type': 'LineString', 'coordinates': line},
        'properties': {'angle': angleList[index]}
    }
    outShp.write(feature)
outShp.close()

# Output GeoJSON
outJson = fiona.open('Shp/croprows.geojson', mode='w', driver='GeoJSON', schema=schema, crs=imgRaster.crs)
for index, line in enumerate(totalLines):
    feature = {
        'geometry': {'type': 'LineString', 'coordinates': line},
        'properties': {'angle': angleList[index]}
    }
    outJson.write(feature)
outJson.close()

# Read the shapefile
df = gpd.read_file('Shp/croprows.shp')

# Get the most common angle
most_common_angle = df['angle'].mode()[0]

# Filter the lines with the most common angle
df_filtered = df[df['angle'] == most_common_angle]

# Plot the original image and the filtered lines side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# Plot original image
ax1.imshow(im, cmap='gray')
ax1.set_title('Imagen original')
ax1.axis('off')

# Plot filtered lines
df_filtered.plot(column='angle', cmap='RdBu', ax=ax2)
ax2.set_title(f'Líneas con el ángulo más común: {most_common_angle} grados')

plt.tight_layout()
plt.show()
