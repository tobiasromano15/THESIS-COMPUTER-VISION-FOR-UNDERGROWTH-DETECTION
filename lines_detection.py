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
fig = plt.figure(figsize=(12,8))
plt.imshow(im)
#plt.show()

# Apply Canny edge detection
edges1 = feature.canny(im)
edges2 = feature.canny(im, sigma=3)

# Display the results
fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(18, 6), sharex=True, sharey=True)

ax1.imshow(im, cmap=plt.cm.gray)
ax1.axis('off')
ax1.set_title('noisy image', fontsize=20)

ax2.imshow(edges1, cmap=plt.cm.gray)
ax2.axis('off')
ax2.set_title(r'Canny filter, $\sigma=1$', fontsize=20)

ax3.imshow(edges2, cmap=plt.cm.gray)
ax3.axis('off')
ax3.set_title(r'Canny filter, $\sigma=3$', fontsize=20)

fig.tight_layout()

#plt.show()

# Use the Canny edge detection result with sigma=3
selImage = edges2

# Classic straight-line Hough transform
# Set a precision of 2 degrees
precision = 2

tested_angles = np.linspace(-np.pi / 2, np.pi / 2, int(180 / precision), endpoint=False)
h, theta, d = hough_line(selImage, theta=tested_angles)

# Generating figure 1
fig = plt.figure(figsize=(18, 16))
gs = gridspec.GridSpec(2,2)

ax0 = plt.subplot(gs[0,0])
ax0.imshow(selImage, cmap=cm.YlGnBu)
ax0.set_title('Input image')
ax0.set_axis_off()

ax1 = plt.subplot(gs[:,1])
angle_step = 0.5 * np.diff(theta).mean()
d_step = 0.5 * np.diff(d).mean()
bounds = [np.rad2deg(theta[0] - angle_step),
          np.rad2deg(theta[-1] + angle_step),
          d[-1] + d_step, d[0] - d_step]
ax1.imshow(np.log(1 + h), extent=bounds, cmap=cm.YlGn, aspect=1 / 1.5)
ax1.set_title('Hough transform')
ax1.set_xlabel('Angles (degrees)')
ax1.set_ylabel('Distance (pixels)')
ax1.axis('image')
ax1.set_aspect(.2)

ax2 = plt.subplot(gs[1,0])
ax2.imshow(selImage, cmap=cm.YlGn)
ax2.set_ylim((selImage.shape[0], 0))
ax2.set_xlim((0, selImage.shape[1]))
ax2.set_axis_off()
ax2.set_title('Detected lines')

for _, angle, dist in zip(*hough_line_peaks(h, theta, d)):
    (x0, y0) = dist * np.array([np.cos(angle), np.sin(angle)])
    ax2.axline((x0, y0), slope=np.tan(angle + np.pi/2))

plt.tight_layout()
#plt.show()

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

# Plot the filtered lines
fig, ax = plt.subplots(figsize=(12,8))
df_filtered.plot(column='angle', cmap='RdBu', ax=ax)
plt.title(f'Lines with the most common angle: {most_common_angle} degrees')
plt.show()