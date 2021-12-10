# Import libraries
import os
import pandas as pd
import geopandas as gpd

# Change working directory
wd = 'D:/'
os.chdir(wd)

# Read site info from observation data
dfs = []
for param in ['tn', 'tp']:
    df = pd.read_csv(f'est_water_qual/data/kese/{param}_obs_yearly.csv')
    dfs.append(df)
obs = pd.concat(dfs).drop_duplicates(subset='site_code').reset_index(drop=True)

# Load catchments of observations sites
catchments = gpd.read_file('est_water_qual/data/catchments/catchments.shp')

# Extract catchments for sites used in the model
catchments = catchments[catchments['site_code'].isin(obs['site_code'].unique())].reset_index(drop=True)

# Write to GPKG
catchments.to_file('est_water_qual/data/catchments/site_catchments.gpkg', driver='GPKG', crs=3301)
