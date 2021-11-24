# Import libraries
import sys
import os
import pathlib

import geopandas as gpd
from osgeo import gdal

from utils import get_zone, fp_to_lulc_data, get_lulc_class_val

# Input arguments
wd = sys.argv[1]
zone_id = int(sys.argv[2])

# Change working directory
os.chdir(wd)

# Get zone
zone = get_zone(zone_id)

# Read LULC data
data = gpd.read_file(fp_to_lulc_data(zone_id), mask=zone, layer='landuse_all')

# Add column with LULC class values
data['class_val'] = data['lulc'].apply(get_lulc_class_val)

# Write to GPKG
fp_to_gpkg = f'/vsimem/lulc_5m_pzone_{zone_id}.gpkg'
data.to_file(fp_to_gpkg)

# Create zonal raster and export as GeoTIFF
filename = os.path.splitext(os.path.basename(fp_to_gpkg))[0] + '.tif'
fp = None
cwd = os.getcwd()
if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
    fp = os.path.join(cwd, 'holgerv/lulc', filename)
elif pathlib.Path(cwd) == pathlib.Path('D:/'):
    fp = os.path.join(cwd, 'lulc', filename)
gdal.Rasterize(
    fp, fp_to_gpkg, outputType=gdal.GDT_Int16, outputBounds=zone.total_bounds, outputSRS='epsg:3301',
    xRes=5, yRes=5, attribute='class_val', creationOptions=['COMPRESS=LZW', 'PREDICTOR=2']
)
