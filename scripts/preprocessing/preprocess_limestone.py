# Import libraries
import sys
import os
import pathlib

from osgeo import gdal

from utils import get_zone, fp_to_limestone_data

# Input arguments
wd = sys.argv[1]
zone_id = int(sys.argv[2])

# Change working directory
os.chdir(wd)

# Get zone
zone = get_zone(zone_id)

# Create zonal raster and export as GeoTIFF
filename = f'limestone_5m_pzone_{zone_id}.tif'
fp = None
cwd = os.getcwd()
if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
    fp = os.path.join(cwd, 'holgerv/geology/limestone', filename)
elif pathlib.Path(cwd) == pathlib.Path('D:/'):
    fp = os.path.join(cwd, 'geology/limestone', filename)
gdal.Rasterize(
    fp, fp_to_limestone_data(), outputType=gdal.GDT_Int16, outputBounds=zone.total_bounds, outputSRS='epsg:3301',
    xRes=5, yRes=5, noData=0, burnValues=1, creationOptions=['COMPRESS=LZW', 'PREDICTOR=2']
)
