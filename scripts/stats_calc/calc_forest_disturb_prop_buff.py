# Import libraries
import sys
import os

import geopandas as gpd
from osgeo import gdal
from rasterstats import zonal_stats
import numpy as np
import pandas as pd

from utils import get_catchment, load_streams, fp_to_predictor_raster, export_stats

# Input arguments
wd = sys.argv[1]
site_code = sys.argv[2]
predictor = 'forest_disturb'
buff_dist = int(sys.argv[3])

# Change working directory
os.chdir(wd)

# Get catchment
catchment = get_catchment(site_code)

# Load streams
streams = load_streams(site_code)

# Buffer streams
buffers = gpd.GeoDataFrame(geometry=streams.buffer(buff_dist), crs=streams.crs)

# Clip buffers
buffers_clip = gpd.clip(buffers, catchment, keep_geom_type=True).reset_index(drop=True)
buffers_clip['site_code'] = site_code

# Calculate proportion
years = range(2016, 2021)
proportions = []
if not buffers_clip.empty:
    band_num = 1
    ds = gdal.Open(fp_to_predictor_raster(site_code, predictor))
    no_data = ds.GetRasterBand(band_num).GetNoDataValue()
    if no_data is None:
        no_data = np.nan
    stats = zonal_stats(
        buffers_clip.dissolve(by='site_code').reset_index(drop=True), fp_to_predictor_raster(site_code, predictor),
        band_num=band_num, nodata=no_data, stats=['count'], categorical=True
    )
    for year in years:
        prop = 0
        if year in stats[0].keys():
            prop = stats[0][year] * 5**2 / buffers_clip.area.sum()
        proportions.append(prop)
else:
    prop = 0
    proportions = [prop for i in range(len(years))]

# Create DataFrame of stats
stats_df = pd.DataFrame(list(zip(proportions, years)), columns=[f'{predictor}_prop_buff_{buff_dist}', 'year'])
stats_df.insert(0, 'site_code', site_code)

# Export stats to CSV
export_stats(stats_df, f'{predictor}_prop_buff_{buff_dist}')
