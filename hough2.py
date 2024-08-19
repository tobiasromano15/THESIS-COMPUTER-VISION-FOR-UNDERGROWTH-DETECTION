import os
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib import cm, gridspec

import rasterio
import geopandas as gpd
from shapely.geometry import LineString
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
            partialLine.append((x, y*2))
        totalLines.append(LineString(partialLine))
        if math.degrees(angle + np.pi / 2) > 90:
            angleList.append(360 - math.degrees(angle + np.pi / 2))
        else:
            angleList.append(math.degrees(angle + np.pi / 2))

    # Create a GeoDataFrame to store the lines and angles in memory
    gdf = gpd.GeoDataFrame({'geometry': totalLines, 'angle': angleList}, crs=imgRaster.crs)

    # Calculate the most common angle
    most_common_angle = gdf['angle'].mode()[0]

    # Filter lines that are within the ±3 degrees range of the most common angle
    angle_tolerance = 3
    df_filtered = gdf[(gdf['angle'] >= most_common_angle - angle_tolerance) &
                      (gdf['angle'] <= most_common_angle + angle_tolerance)]

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
#process_image_and_save("C:/Users/Tobi/Desktop/TESIS/plantitas/DJI_0381.JPG")
