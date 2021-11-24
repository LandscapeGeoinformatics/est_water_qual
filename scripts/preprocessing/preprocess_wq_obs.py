# Import libraries
import sys
import os
import numpy as np
import pandas as pd
import geopandas as gpd

# Input arguments
wd = 'D:/'
param = sys.argv[1]

# Change working directory
os.chdir(wd)

# Load streams
streams = gpd.read_file('est_water_qual/data/eelis/eelis_streams.gpkg', ignore_geometry=True)

# Read observation data, drop rows with missing site codes or coordinates and keep only sites located at streams
fp = f'est_water_qual/data/kese/{param}_obs.csv'
dtypes = {
    'Seirekoha KKR': object,
    'Seirekoha nimi': object,
    'Sisestatud x L-EST97': np.float64,
    'Sisestatud y L-EST97': np.float64,
    'Veekogu KKR': object,
    'Proovi / vaatluse  kood': object,
    'Seireaeg': object,
    'Arvväärtus': object,
    'Väärtuse ühik': object
}
obs = pd.read_csv(fp, sep=';', usecols=dtypes.keys(), dtype=dtypes, quotechar='"').\
    rename(
    columns={
        'Seirekoha KKR': 'site_code',
        'Seirekoha nimi': 'site_name',
        'Sisestatud y L-EST97': 'x',
        'Sisestatud x L-EST97': 'y',
        'Veekogu KKR': 'waterbody_code',
        'Proovi / vaatluse  kood': 'obs_code',
        'Seireaeg': 'obs_time',
        'Arvväärtus': 'obs_value',
        'Väärtuse ühik': 'obs_unit'
    })\
    .dropna(subset=['site_code', 'x', 'y'])\
    .pipe(lambda df: df.loc[df['waterbody_code'].isin(streams['kr_kood'].unique())])\
    .reset_index(drop=True)

# Convert observation values
obs['obs_value'] = obs['obs_value'].str.replace(',', '.').astype(np.float64)

# Add date of observation as new column
obs['obs_date'] = pd.to_datetime(obs['obs_time']).dt.strftime('%Y-%m-%d')

# Calculate daily mean values
obs_daily = obs.groupby(['site_code', 'obs_date'])['obs_value'].mean().reset_index()

# Extract month and year from date
obs_daily['obs_month'] = pd.to_datetime(obs_daily['obs_date']).dt.month
obs_daily['obs_year'] = pd.to_datetime(obs_daily['obs_date']).dt.year

# Calculate monthly mean values
obs_monthly = obs_daily.groupby(['site_code', 'obs_year', 'obs_month'])['obs_value'].mean().reset_index()
obs_monthly['obs_value'] = obs_monthly['obs_value'].round(3)

# Extract sites with at least four distinct monthly observations in at least one of the years
sites_four_distinct = obs_monthly.groupby(['site_code', 'obs_year'])['obs_value'].agg(['count'])\
    .pipe(lambda df: df.loc[df['count'] >= 4]).reset_index()['site_code'].unique()

# Extract site locations based on the aforementioned criterion
site_locations = obs[['site_code', 'x', 'y', 'waterbody_code']]\
    .drop_duplicates('site_code')\
    .pipe(lambda df: df.loc[df['site_code'].isin(sites_four_distinct)])\
    .reset_index(drop=True)

# Convert to GeoDataFrame and write to GPKG
site_points = gpd.GeoDataFrame(
    site_locations, geometry=gpd.points_from_xy(site_locations['x'], site_locations['y']), crs=3301
)
site_points.to_file('est_water_qual/data/kese/obs_sites.gpkg', layer=f'{param}_sites', driver='GPKG')

# Extract monthly observations based on the aforementioned criterion and write to CSV
obs_monthly[obs_monthly['site_code'].isin(sites_four_distinct)]\
    .reset_index(drop=True)\
    .to_csv(f'est_water_qual/data/kese/{param}_obs_monthly.csv', sep=',', index=False)

# Calculate yearly mean values
obs_yearly = obs_monthly.groupby(['site_code', 'obs_year'])['obs_value'].mean().reset_index()
obs_yearly['obs_value'] = obs_yearly['obs_value'].round(3)

# Extract yearly observations based on the aforementioned criterion and write to CSV
obs_yearly[obs_yearly['site_code'].isin(sites_four_distinct)]\
    .reset_index(drop=True)\
    .to_csv(f'est_water_qual/data/kese/{param}_obs_yearly.csv', sep=',', index=False)
