# Import libraries
import sys
import os
import pathlib

import pandas as pd

# Input arguments
wd = sys.argv[1]
param = sys.argv[2]

# Change working directory
os.chdir(wd)

# Get list of predictors
dir_path = None
cwd = os.getcwd()
if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\export.hpc.ut.ee\gis')]:
    dir_path = 'holgerv/est_water_qual/data/predictors'
elif pathlib.Path(cwd) == pathlib.Path('D:/'):
    dir_path = 'est_water_qual/data/predictors'
predictors = [item for item in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, item))]

# Create empty DataFrame for the predictors
df_predictors = pd.DataFrame(columns=['site_code', 'year'])

# Merge predictors with the empty DataFrame
for predictor in predictors:
    fp = os.path.join(cwd, dir_path, predictor, f'{predictor}_stats.csv')
    if os.path.exists(fp):
        df = pd.read_csv(fp, sep=',')
        if 'arable_prop_buff' in predictor:
            df = df.rename(columns={'arable_prop': predictor})
        df_predictors = df_predictors.merge(df, how='outer', on=['site_code', 'year'])

# Round the values of predictors
for col in df_predictors.columns:
    if col not in ['site_code', 'year']:
        df_predictors[col] = df_predictors[col].round(3)

# Read observation data
fp_obs = None
if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\export.hpc.ut.ee\gis')]:
    fp_obs = os.path.join(cwd, f'holgerv/est_water_qual/data/kese/{param}_obs_yearly.csv')
elif pathlib.Path(cwd) == pathlib.Path('D:/'):
    out_fp = os.path.join(cwd, f'est_water_qual/data/kese/{param}_obs_yearly.csv')
df_obs = pd.read_csv(fp_obs, sep=',')

# Create ML input
ml_input = df_obs\
    .merge(df_predictors, how='left', left_on=['site_code', 'obs_year'], right_on=['site_code', 'year'])\
    .drop('year', axis=1)\
    .reset_index(drop=True)
ml_input.insert(2, 'parameter', param.upper())

# Write to CSV
out_name = f'{param}_ml_input.csv'
if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\export.hpc.ut.ee\gis')]:
    out_fp = os.path.join(cwd, 'holgerv/est_water_qual/model', out_name)
elif pathlib.Path(cwd) == pathlib.Path('D:/'):
    out_fp = os.path.join(cwd, 'est_water_qual/model', out_name)
ml_input.to_csv(out_fp, sep=',', index=False)
