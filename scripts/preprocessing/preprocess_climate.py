# Import libraries
import sys
import os

import xarray as xr
from osgeo import gdal
import numpy as np

from utils import get_zone, fp_to_climate_data, fp_to_zonal_raster

# Input variables
wd = sys.argv[1]
zone_id = int(sys.argv[2])
predictor = sys.argv[3]

# Change working directory
os.chdir(wd)

# Get zone
zone = get_zone(zone_id)

# Open dataset and set CRS
ds = xr.open_dataset(fp_to_climate_data(predictor))
ds.rio.set_crs(4326)

# Convert units
ds_converted = None
if predictor in ['temp_max', 'temp_mean', 'temp_min']:
    ds_converted = ds - 273.15
elif predictor == 'precip':
    ds_converted = ds.shift(time=-1).dropna(dim='time', how='all') * 1000
elif predictor == 'snow_depth':
    ds_converted = ds.shift(time=-1).dropna(dim='time', how='all') * 100

# Resample to daily data
ds_resampled = None
if predictor in ['temp_max', 'precip']:
    ds_resampled = ds_converted.resample(time='1D').max('time')
elif predictor in ['temp_mean', 'snow_depth']:
    ds_resampled = ds_converted.resample(time='1D').mean('time')
elif predictor == 'temp_min':
    ds_resampled = ds_converted.resample(time='1D').min('time')

# Group by year
ds_grouped = None
if predictor == 'temp_max':
    ds_grouped = ds_resampled.groupby('time.year').max('time', skipna=False)
elif predictor in ['temp_mean', 'snow_depth']:
    ds_grouped = ds_resampled.groupby('time.year').mean('time', skipna=False)
elif predictor == 'temp_min':
    ds_grouped = ds_resampled.groupby('time.year').min('time', skipna=False)
elif predictor == 'precip':
    ds_grouped = ds_resampled.groupby('time.year').sum('time', skipna=False)

# Create annual zonal raster layers and collect them as VRT input
vrt_input = []
for year in range(2016, 2021):
    fp_to_annual_raster = f'/vsimem/{predictor}_{year}.tif'
    ds_grouped.sel(year=year).rio.to_raster(fp_to_annual_raster)
    fp_to_annual_zonal_raster = f'/vsimem/{predictor}_5m_pzone_{zone_id}_{year}.tif'
    gdal.Warp(
        fp_to_annual_zonal_raster, fp_to_annual_raster, outputBounds=zone.total_bounds, outputBoundsSRS='epsg:3301',
        xRes=5, yRes=5, srcSRS='epsg:4326', dstSRS='epsg:3301', outputType=gdal.GDT_Float32
    )
    vrt_input.append(fp_to_annual_zonal_raster)

# Create VRT from annual raster layers
fp_to_vrt = f'/vsimem/{predictor}_5m_pzone_{zone_id}.vrt'
ds = gdal.BuildVRT(fp_to_vrt, vrt_input, separate=True)
years = range(2016, 2021)
for i, year in zip(range(1, len(years) + 1), years):
    ds.GetRasterBand(i).SetDescription(str(year))
ds = None

# Export VRT as GeoTIFF
gdal.Translate(
    fp_to_zonal_raster(predictor, zone_id), fp_to_vrt, creationOptions=['COMPRESS=LZW', 'PREDICTOR=2'], noData=np.nan
)
