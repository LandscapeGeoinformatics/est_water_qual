# Import libraries
import sys
import os
from joblib import load

import pandas as pd
import geopandas as gpd

from utils import get_model_dir


# Create GeoDataFrame with results from the model
def results_to_gdf(catchments: gpd.GeoDataFrame, column: object) -> gpd.GeoDataFrame:
    catchments_grouped = catchments.groupby('site_code')[column].mean().reset_index()
    catchments_grouped = catchments_grouped.merge(catchments[['site_code', 'geometry']], how='left', on='site_code')
    catchments_grouped = catchments_grouped.drop_duplicates('site_code').reset_index(drop=True)
    gdf = gpd.GeoDataFrame(catchments_grouped, geometry='geometry', crs=3301)
    gdf['area'] = gdf.area
    return gdf


# Input arguments
wd = sys.argv[1]
feat_set = sys.argv[2]

# Parameter
param = feat_set.split('_')[0]

# Change working directory
os.chdir(wd)

# Model directory
param = feat_set.split('_')[0]
version = feat_set.split('_')[2]
model = f'{param}_model_{version}'
model_dir = get_model_dir(model)

# Read ML input
ml_input = pd.read_csv(f'D:/est_water_qual/model/{model}/{feat_set}_ml_input.csv', sep=',')

# Extract features and target
X = ml_input.iloc[:, 4:]
y = ml_input['obs_value']

# Read training and test data
X_train = pd.read_csv(f'{model_dir}/{feat_set}_feat_train.csv', sep=',').drop('index', axis=1)
X_test = pd.read_csv(f'{model_dir}/{feat_set}_feat_test.csv', sep=',').drop('index', axis=1)
y_train = pd.read_csv(f'{model_dir}/{feat_set}_target_train.csv', sep=',')
y_test = pd.read_csv(f'{model_dir}/{feat_set}_target_test.csv', sep=',')

# Load model
regressor = load(f'{model_dir}/{model}.joblib')

# Read results
obs_vs_pred = pd.read_csv(f'{model_dir}/{model}_obs_vs_pred.csv', sep=',')

# Read catchments
catchments = gpd.read_file('D:/est_water_qual/data/catchments/site_catchments.gpkg')
catchments = catchments\
    .merge(obs_vs_pred, how='right', on='site_code')\
    .dropna(subset=['ratio'])\
    .reset_index(drop=True)

# Export ratios to GPKG
gdf = results_to_gdf(catchments, 'ratio')
gdf.to_file('D:/est_water_qual/model/results.gpkg', layer=f'{model}_mean_ratios', driver='GPKG', crs=3301)

# Export residuals to GPKG
gdf = results_to_gdf(catchments, 'residual')
gdf.to_file('D:/est_water_qual/model/results.gpkg', layer=f'{model}_mean_residuals', driver='GPKG', crs=3301)
