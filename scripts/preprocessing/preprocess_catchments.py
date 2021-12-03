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
    df = pd.read_csv(f'est_water_qual/data/kese/{param}_obs.csv', sep=';', usecols=['Seirekoha KKR', 'Veekogu KKR'])
    dfs.append(df)
obs = pd.concat(dfs).\
    drop_duplicates(subset='Seirekoha KKR').\
    reset_index(drop=True).\
    rename(columns={'Seirekoha KKR': 'site_code', 'Veekogu KKR': 'waterbody_code'})

# Load catchments of hydrochemistry stations
hydrochem_catchments = gpd.read_file('est_water_qual/data/catchments/Valglad/Hüdrokeemia_valglad.shp')
hydrochem_catchments = hydrochem_catchments.\
    drop(['nimi', 'Shape_Area'], axis=1).rename(columns={'kkr_kood': 'site_code'})

# Load catchments of observations sites
obs_catchments = gpd.read_file('est_water_qual/data/catchments/valglad_195_tu/valglad_tu_kõik_koos.shp')
obs_catchments = obs_catchments.drop(['gridcode', 'veekogu'], axis=1).rename(columns={'seirekoht': 'site_code'})

# Concatenate catchments
catchments = pd.concat([hydrochem_catchments, obs_catchments])\
    .drop_duplicates(subset='site_code')\
    .reset_index(drop=True)

# Merge catchments with site info
catchments = catchments.merge(obs, how='left', on='site_code')

# Drop catchments of River Narva
catchments = catchments[catchments['waterbody_code'] != 'VEE1062200'].reset_index(drop=True)

# Write to GPKG
catchments.to_file('est_water_qual/data/catchments/catchments.gpkg', driver='GPKG')
