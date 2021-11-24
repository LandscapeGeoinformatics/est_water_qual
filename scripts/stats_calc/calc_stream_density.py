# Import libraries
import sys
import os

import geopandas as gpd
import pandas as pd

from utils import get_catchment, load_streams, export_stats

# Input arguments
wd = sys.argv[1]
site_code = sys.argv[2]
predictor = 'stream_density'

# Change working directory
os.chdir(wd)

# Get catchment
catchment = get_catchment(site_code)

# Load streams
streams = load_streams(site_code)

# Clip streams
streams_clip = gpd.clip(streams, catchment, keep_geom_type=True).reset_index(drop=True)

# Calculate proportion
stream_density = 0
if not streams_clip.empty:
    stream_density = streams_clip.length.sum() / catchment.area.sum()

# Create DataFrame of stats
years = range(2016, 2021)
stats = [stream_density for i in range(len(years))]
stats_df = pd.DataFrame(list(zip(stats, years)), columns=[f'{predictor}', 'year'])
stats_df.insert(0, 'site_code', site_code)

# Export stats to CSV
export_stats(stats_df, f'{predictor}')
