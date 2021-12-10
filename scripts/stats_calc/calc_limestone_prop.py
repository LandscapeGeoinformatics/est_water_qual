# Import libraries
import sys
import os

from osgeo import gdal
from rasterstats import zonal_stats
import numpy as np
import pandas as pd

from utils import get_catchment, get_band_num, fp_to_predictor_raster, get_lulc_class_val, export_stats

# Input arguments
wd = sys.argv[1]
site_code = sys.argv[2]
predictor = 'limestone'

# Change working directory
os.chdir(wd)

# Get catchment
catchment = get_catchment(site_code)

# Create DataFrame of stats
stats_dicts = []
for year in range(2016, 2021):
    band_num = get_band_num(predictor, year)
    ds = gdal.Open(fp_to_predictor_raster(site_code, predictor))
    no_data = ds.GetRasterBand(band_num).GetNoDataValue()
    if no_data is None:
        no_data = np.nan
    stats = zonal_stats(
        catchment, fp_to_predictor_raster(site_code, predictor), band_num=1, nodata=no_data, stats=['count'],
        categorical=True
    )
    prop = 0
    if 1 in stats[0].keys():
        prop = stats[0][1] * 5**2 / catchment.area.sum()
    stats_dict = {
        f'{predictor}_prop': prop,
        'year': year
    }
    stats_dicts.append(stats_dict)
stats_df = pd.DataFrame(stats_dicts)
stats_df.insert(0, 'site_code', site_code)

# Export stats to CSV
export_stats(stats_df, f'{predictor}_prop')
