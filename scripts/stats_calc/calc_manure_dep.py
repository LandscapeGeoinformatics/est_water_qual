# Import libraries
import sys
import os
import pathlib

import geopandas as gpd
import pandas as pd

from utils import get_catchment, fp_to_counties, export_stats

# Input arguments
wd = sys.argv[1]
site_code = sys.argv[2]
predictor = sys.argv[3]

# Change working directory
os.chdir(wd)

# Get catchment
catchment = get_catchment(site_code)

# Load counties
counties = gpd.read_file(fp_to_counties()).drop('MKOOD', axis=1).rename(columns={'MNIMI': 'county'})

# Clip counties
counties_clip = gpd.clip(counties, catchment)\
    .reset_index(drop=True)\
    .pipe(lambda df: df.assign(area_ha=df.area / 10000))

# Read manure data
cwd = os.getcwd()
filename = f'manure/{predictor}_kg_per_ha.csv'
if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
    fp = os.path.join(cwd, 'holgerv/manure', filename)
elif pathlib.Path(cwd) == pathlib.Path('D:/'):
    fp = os.path.join(cwd, 'manure', filename)
fp = os.path.join(os.getcwd(), f'{predictor}_kg_per_ha.csv')
manure = pd.read_csv(fp, sep=',')

# Merge counties with manure
counties_manure = counties_clip[['county', 'area_ha']].merge(manure, how='left', on='county').reset_index(drop=True)

# Calculate amount of nutrient in kg
counties_manure[f'{predictor}_kg'] = counties_manure[f'{predictor}_kg_per_ha'] * counties_manure['area_ha']

# Calculate amount of nutrient per year in catchment
manure_yearly = counties_manure.groupby('year')[f'{predictor}_kg'].sum().reset_index()
manure_yearly[predictor] = manure_yearly[f'{predictor}_kg'] / (catchment.area.sum() / 10000)
manure_yearly.insert(0, 'site_code', site_code)

# Create DataFrame of stats and export to CSV
stats_df = manure_yearly.drop(f'{predictor}_kg', axis=1)
export_stats(stats_df, predictor)
