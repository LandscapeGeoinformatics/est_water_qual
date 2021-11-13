# Import libraries
import sys
import os

from utils import export_zonal_stats

# Input arguments
wd = sys.argv[1]
site_code = sys.argv[2]
predictor = sys.argv[3]

# Change working directory
os.chdir(wd)

# Calculate and export zonal stats
export_zonal_stats(site_code, predictor)
