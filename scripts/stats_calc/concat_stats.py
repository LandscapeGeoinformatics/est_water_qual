# Import libraries
import sys
import os
import pathlib
import glob

import pandas as pd

# Input arguments
wd = sys.argv[1]
predictor = sys.argv[2]

# Change working directory
os.chdir(wd)

# Get list of files
files = None
cwd = os.getcwd()
if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
    files = glob.glob(f'holgerv/est_water_qual/data/predictors/{predictor}/*_{predictor}_stats.csv')
elif pathlib.Path(cwd) == pathlib.Path('D:/'):
    files = glob.glob(f'est_water_qual/data/predictors/{predictor}/*_{predictor}_stats.csv')

# Create DataFrame
stats_df = pd.concat([pd.read_csv(file, sep=',') for file in files], ignore_index=True)

# Export to CSV
stats_df.to_csv(f'holgerv/est_water_qual/data/predictors/{predictor}/{predictor}_stats.csv', sep=',', index=False)
