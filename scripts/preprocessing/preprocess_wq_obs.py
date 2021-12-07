# Import libraries
import sys
import os

import geopandas as gpd
import numpy as np
import pandas as pd

from utils import fp_to_streams


# Read water quality observation data
def read_wq_obs(param):
    streams = gpd.read_file(fp_to_streams(), ignore_geometry=True)
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
    obs = pd.read_csv(fp, sep=';', usecols=dtypes.keys(), dtype=dtypes, quotechar='"'). \
        rename(
        columns={
            'Seirekoha KKR': 'site_code',
            'Seirekoha nimi': 'site_name',
            'Sisestatud y L-EST97': 'x',
            'Sisestatud x L-EST97': 'y',
            'Veekogu KKR': 'wb_code',
            'Proovi / vaatluse  kood': 'obs_code',
            'Seireaeg': 'obs_time',
            'Arvväärtus': 'obs_value',
            'Väärtuse ühik': 'obs_unit'
        }) \
        .dropna(subset=['site_code', 'x', 'y']) \
        .pipe(lambda df: df.loc[df['wb_code'].isin(streams['kr_kood'].unique())]) \
        .reset_index(drop=True)

    # Drop observations from sites of River Narva
    obs = obs[obs['wb_code'] != 'VEE1062200'].reset_index(drop=True)

    obs['obs_value'] = obs['obs_value'].str.replace(',', '.').astype(np.float64)
    obs['obs_date'] = pd.to_datetime(obs['obs_time']).dt.strftime('%Y-%m-%d')
    obs['obs_month'] = pd.to_datetime(obs['obs_date']).dt.month
    obs['obs_year'] = pd.to_datetime(obs['obs_date']).dt.year
    return obs


# Get daily observation values
def get_daily_obs(param):
    obs = read_wq_obs(param)
    obs_daily = obs.groupby(['site_code', 'obs_year', 'obs_month', 'obs_date'])['obs_value'].mean().reset_index()
    obs_daily['obs_value'] = obs_daily['obs_value'].round(3)
    return obs_daily


# Get monthly observation values
def get_monthly_obs(obs_daily):
    obs_monthly = obs_daily.groupby(['site_code', 'obs_year', 'obs_month'])['obs_value'].mean().reset_index()
    obs_monthly['obs_value'] = obs_monthly['obs_value'].round(3)
    return obs_monthly


# Get yearly observation values
def get_yearly_obs(obs_daily):
    obs_yearly = obs_daily.groupby(['site_code', 'obs_year'])['obs_value'].mean().reset_index()
    obs_yearly['obs_value'] = obs_yearly['obs_value'].round(3)
    return obs_yearly


# Input arguments
wd = sys.argv[1]
param = sys.argv[2]

# Change working directory
os.chdir(wd)

# Get daily observation values
obs_daily = get_daily_obs(param)

# Remove the site with extreme outliers
obs_daily = obs_daily[obs_daily['site_code'] != 'SJA2858025'].reset_index(drop=True)

# Get monthly observation values
obs_monthly = get_monthly_obs(obs_daily)

# Extract sites with at least four distinct monthly observations in at least one of the years
four_distinct_monthly = obs_monthly.groupby(['site_code', 'obs_year'])['obs_value'].agg(['count'])\
    .pipe(lambda df: df.loc[df['count'] >= 4]).reset_index()['site_code'].unique()

# Extract daily observations based on the aforementioned criterion
obs_daily_four_distinct = obs_daily[obs_daily['site_code'].isin(four_distinct_monthly)].reset_index(drop=True)

# Get yearly observation values
obs_yearly = get_yearly_obs(obs_daily_four_distinct)

# Export yearly values to CSV
obs_yearly.to_csv(f'est_water_qual/data/kese/{param}_obs_yearly.csv', sep=',', index=False)

# Read raw water quality observation data
obs = read_wq_obs(param)

# Extract site locations of yearly observations from raw data
site_locations = obs[['site_code', 'x', 'y', 'wb_code']]\
    .drop_duplicates('site_code')\
    .pipe(lambda df: df.loc[df['site_code'].isin(obs_yearly['site_code'].unique())])\
    .reset_index(drop=True)

# Convert to GeoDataFrame and write to GPKG
site_points = gpd.GeoDataFrame(
    site_locations, geometry=gpd.points_from_xy(site_locations['x'], site_locations['y']), crs=3301
)
site_points.to_file('est_water_qual/data/kese/obs_site_points.gpkg', layer=f'{param}_site_points', driver='GPKG')
