# Import libraries
import sys
import os

import numpy as np
from osgeo import gdal
import rasterio
from rasterio.fill import fillnodata

from utils import get_zone, fp_to_dem_data, fp_to_zonal_raster

# Input arguments
wd = sys.argv[1]
zone_id = int(sys.argv[2])
predictor = sys.argv[3]

# Change working directory
os.chdir(wd)

# Get zone
zone = get_zone(zone_id)

# Create and export zonal raster
ds = gdal.Open(fp_to_dem_data(zone_id))
fp = fp_to_zonal_raster(predictor, zone_id)
if zone_id == 21:
    fp = os.path.join('/vsimem/', os.path.basename(fp).replace('tif', 'vrt'))
gdal.Warp(
    fp, ds, outputBounds=zone.total_bounds, outputBoundsSRS='epsg:3301', xRes=5, yRes=5, srcSRS='epsg:3301',
    dstSRS='epsg:3301', outputType=gdal.GDT_Float32, creationOptions=['COMPRESS=LZW', 'PREDICTOR=2'],
    srcNodata=ds.GetRasterBand(1).GetNoDataValue(), dstNodata=np.nan
)
ds = None

# Fill missing values in processing zone 21
if zone_id == 21:
    with rasterio.open(fp) as src:
        profile = src.profile.copy()
        profile.update({'driver': 'GTiff'})
        array = src.read(1)
        mask = src.read_masks(1)
        filled = fillnodata(array, mask, max_search_distance=2000)
    with rasterio.open(fp_to_zonal_raster(predictor, zone_id), 'w', **profile) as dst:
        dst.write_band(1, filled)
