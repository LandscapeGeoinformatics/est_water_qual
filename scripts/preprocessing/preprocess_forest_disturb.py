# Import libraries
import sys
import os

from osgeo import gdal

from utils import get_zone, fp_to_forest_disturb_data, fp_to_zonal_raster

# Input arguments
wd = sys.argv[1]
zone_id = int(sys.argv[2])
predictor = 'forest_disturb'

# Change working directory
os.chdir(wd)

# Get zone
zone = get_zone(zone_id)

# Create and export zonal raster
ds = gdal.Open(fp_to_forest_disturb_data())
fp = fp_to_zonal_raster(predictor, zone_id)
gdal.Warp(
    fp, ds, outputBounds=zone.total_bounds, outputBoundsSRS='epsg:3301', xRes=5, yRes=5, srcSRS='epsg:3035',
    dstSRS='epsg:3301', outputType=gdal.GDT_Int16, creationOptions=['COMPRESS=LZW', 'PREDICTOR=2'],
    srcNodata=ds.GetRasterBand(1).GetNoDataValue(), dstNodata=0
)
ds = None
