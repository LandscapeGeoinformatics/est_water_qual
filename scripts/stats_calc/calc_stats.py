# Import libraries
import sys
import os

from utils import zonal_stats_df, export_stats

# Input arguments
wd = sys.argv[1]
site_code = sys.argv[2]
predictor = sys.argv[3]

# Change working directory
os.chdir(wd)

# Calculate and export zonal stats
export_stats(zonal_stats_df(site_code, predictor), predictor)
