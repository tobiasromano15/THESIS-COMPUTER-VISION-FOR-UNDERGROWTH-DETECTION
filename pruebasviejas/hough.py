import os
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib import cm, gridspec

# Geospatial libraries
import rasterio
import fiona
import geopandas as gpd
from shapely.geometry import LineString

# Machine learning libraries
from skimage.feature import canny
from skimage.transform import hough_line, hough_line_peaks


def process_image_and_save(input_filename):
    # Load the raster image with all channels
    imgRaster = rasterio.open(input_filename)
    im = imgRaster.read()

    # Convert the image to a format that can be displayed in color (RGB)
    if im.shape[0] == 3:  # If the image has 3 channels (RGB)
        im_rgb = np.transpose(im, (1, 2, 0))
    else:
        # If the image has more than 3 channels, take the first 3
        im_rgb = np.transpose(im[:3], (1, 2, 0))
    sigma_value = 3  # Puedes ajustar este valor

    # Apply Canny edge detection
    edges1 = canny(im_rgb[:, :, 0])
    edges2 = canny(im_rgb[:, :, 0], sigma=sigma_value)

    # Use the Canny edge detection result with sigma=3
    selImage = edges2

    # Classic straight-line Hough transform
    precision = 2
    tested_angles = np.linspace(-np.pi / 2, np.pi / 2, int(180 / precision), endpoint=False)
    h, theta, d = hough_line(selImage, theta=tested_angles)

    selDiag = selImage.shape[1]
    progRange = range(selDiag)
    totalLines = []
    angleList = []
    for _, angle, dist in zip(*hough_line_peaks(h, theta, d)):
        (x0, y0) = dist * np.array([np.cos(angle), np.sin(angle)])
        if angle in [np.pi / 2, -np.pi / 2]:
            cols = [prog for prog in progRange]
            rows = [y0 for prog in progRange]
        elif angle == 0:
            cols = [x0 for prog in progRange]
            rows = [prog for prog in progRange]
        else:
            c0 = y0 + x0 / np.tan(angle)
            cols = [prog for prog in progRange]
            rows = [col * np.tan(angle + np.pi / 2) + c0 for col in cols]

        partialLine = []
        for col, row in zip(cols, rows):
            x, y = imgRaster.xy(int(row), int(col))
            partialLine.append((x, y))
        totalLines.append(partialLine)
        if math.degrees(angle + np.pi / 2) > 90:
            angleList.append(360 - math.degrees(angle + np.pi / 2))
        else:
            angleList.append(math.degrees(angle + np.pi / 2))

    schema = {
        'properties': {'angle': 'float:16'},
        'geometry': 'LineString'
    }

    output_dir = 'Shp'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with fiona.open(os.path.join(output_dir, 'croprows.shp'), mode='w', driver='ESRI Shapefile', schema=schema,
                    crs=imgRaster.crs) as outShp:
        for index, line in enumerate(totalLines):
            feature = {
                'geometry': {'type': 'LineString', 'coordinates': line},
                'properties': {'angle': angleList[index]}
            }
            outShp.write(feature)

    with fiona.open(os.path.join(output_dir, 'croprows.geojson'), mode='w', driver='GeoJSON', schema=schema,
                    crs=imgRaster.crs) as outJson:
        for index, line in enumerate(totalLines):
            feature = {
                'geometry': {'type': 'LineString', 'coordinates': line},
                'properties': {'angle': angleList[index]}
            }
            outJson.write(feature)

    df = gpd.read_file(os.path.join(output_dir, 'croprows.shp'))

    most_common_angle = df['angle'].mode()[0]

    # Filtra líneas que estén dentro del rango de ±5 grados del ángulo más común
    angle_tolerance = 10
    df_filtered = df[(df['angle'] >= most_common_angle - angle_tolerance) &
                     (df['angle'] <= most_common_angle + angle_tolerance)]

    # Match the dimensions and DPI of the input image
    height, width, _ = im_rgb.shape
    dpi = 100

    fig, ax = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi)

    # Plot original image in color
    ax.imshow(im_rgb, extent=(
        imgRaster.bounds.left, imgRaster.bounds.right,
        imgRaster.bounds.bottom, imgRaster.bounds.top
    ))
    ax.set_xlim(imgRaster.bounds.left, imgRaster.bounds.right)
    ax.set_ylim(imgRaster.bounds.bottom, imgRaster.bounds.top)

    for line in df_filtered['geometry']:
        x, y = line.xy
        ax.plot(x, y, color='red')

    ax.axis('off')  # Remove axis to keep the original image appearance
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(input_filename, bbox_inches='tight', pad_inches=0, dpi=dpi)


# Call the function to process the image and save the result
process_image_and_save('subimagenes/subimage_1_3.png')
