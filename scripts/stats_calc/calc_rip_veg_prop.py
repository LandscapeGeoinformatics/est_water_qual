# Import libraries
import numpy as np
import sys
import os

import geopandas as gpd
import pandas as pd

from utils import get_catchment, fp_to_rip_veg_data, export_stats

# Input arguments
wd = sys.argv[1]
site_code = sys.argv[2]
predictor = sys.argv[3]

# Change working directory
os.chdir(wd)

# Get catchment
catchment = get_catchment(site_code)

# Layer to read
layer = None

# Layer for vegetation in buffers of natural streams
if predictor == 'rip_veg_nat':
    layer = 'LVK_puhverriba_taimkate'
# Layer for vegetation in buffers of drainage ditches
elif predictor == 'rip_veg_drain':
    layer = 'MSR_puhverriba_taimkate'

# Read riparian vegetation data
rip_veg = gpd.read_file(fp_to_rip_veg_data(), mask=catchment, layer=layer)

# Clip data with catchment
rip_veg_clip = gpd.clip(rip_veg, catchment, keep_geom_type=True).reset_index(drop=True)

# Calculate proportion
prop = 0
if not rip_veg_clip.empty:
    rip_veg_clip['Taimk'] = rip_veg_clip['Taimk'].astype(np.int32)
    if 1 in list(rip_veg_clip['Taimk'].unique()):
        prop = rip_veg_clip[rip_veg_clip['Taimk'] == 1].area.sum() / rip_veg_clip.area.sum()

# Create DataFrame of stats
years = range(2016, 2021)
stats = [prop for i in range(len(years))]
stats_df = pd.DataFrame(list(zip(stats, years)), columns=[f'{predictor}_prop', 'year'])
stats_df.insert(0, 'site_code', site_code)

# Export stats to CSV
export_stats(stats_df, f'{predictor}_prop')
