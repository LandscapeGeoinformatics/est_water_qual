# Import libraries
import sys
import os

import numpy as np
from osgeo import gdal

from utils import get_zone, fp_to_soil_data, fp_to_zonal_raster

# Input arguments
wd = sys.argv[1]
zone_id = int(sys.argv[2])
predictor = sys.argv[3]

# Change working directory
os.chdir(wd)

# Get zone
zone = get_zone(zone_id)

# Create zonal raster and export as GeoTIFF
gdal.Rasterize(
    fp_to_zonal_raster(predictor, zone_id), fp_to_soil_data(), outputType=gdal.GDT_Float32,
    outputBounds=zone.total_bounds, outputSRS='epsg:3301', xRes=5, yRes=5, noData=np.nan,
    attribute=f'{predictor}', layers='EstSoil-EH_v1.2c', creationOptions=['COMPRESS=LZW', 'PREDICTOR=2']
)
