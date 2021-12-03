# Import libraries
import sys
import os

import pandas as pd

from utils import load_catchments, get_catchment, export_stats

# Input arguments
wd = sys.argv[1]
predictor = 'area'

# Change working directory
os.chdir(wd)

# Load catchments
catchments = load_catchments()

# Get list of site codes
site_codes = catchments['site_code'].unique()

# Calculate area of catchment
for site_code in site_codes:
    catchment = get_catchment(site_code)
    area = catchment.area.sum()

    # Create DataFrame of stats
    years = range(2016, 2021)
    stats = [area for i in range(len(years))]
    stats_df = pd.DataFrame(list(zip(stats, years)), columns=[f'{predictor}', 'year'])
    stats_df.insert(0, 'site_code', site_code)

    # Export stats to CSV
    export_stats(stats_df, f'{predictor}')
