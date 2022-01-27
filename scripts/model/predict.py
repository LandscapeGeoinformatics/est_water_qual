# Import libraries
import sys
import os
from joblib import load

import pandas as pd
from sklearn.metrics import r2_score

from utils import get_model_dir


# Get NSE
def get_nse(obs_values: pd.Series, pred_values: pd.Series) -> float:
    residuals = obs_values - pred_values
    nse = 1 - ((residuals ** 2).sum() / ((obs_values - obs_values.mean()) ** 2).sum())
    return nse


# Get PBIAS
def get_pbias(obs_values: pd.Series, pred_values: pd.Series) -> float:
    pbias = (pred_values - obs_values).sum() / obs_values.sum()
    return pbias


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
ml_input = pd.read_csv(f'{model_dir}/{feat_set}_ml_input.csv', sep=',')

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

# Predict
Y_train_pred = regressor.predict(X_train)
Y_test_pred = regressor.predict(X_test)

# Create DataFrame from observed and predicted values
y_test_df = pd.DataFrame(y_test.set_index('index'))
y_test_df['pred_value'] = Y_test_pred
y_train_df = pd.DataFrame(y_train.set_index('index'))
y_train_df['pred_value'] = Y_train_pred
obs_vs_pred = ml_input[['site_code']].join(pd.concat([y_test_df, y_train_df]))

# Calculate residuals between observed and predicted values
obs_vs_pred['residual'] = round(obs_vs_pred['obs_value'] - obs_vs_pred['pred_value'], 3)

# Calculate ratio between observed and predicted values and export to CSV
obs_vs_pred['ratio'] = round(obs_vs_pred['obs_value'] / obs_vs_pred['pred_value'], 3)
obs_vs_pred.to_csv(f'{model_dir}/{model}_obs_vs_pred.csv', sep=',', index=False)

# Calculate NSE
nse = get_nse(y_test_df['obs_value'], y_test_df['pred_value'])

# Calculate PBIAS
pbias = get_pbias(y_test_df['obs_value'], y_test_df['pred_value'])

# Get parameters
params = regressor.get_params()

# Collect results into dictionary
test_size = 0.3
results = {
    # 'version_name': version_name,
    'n_features': len(X.columns),
    'test_size': test_size,
    'n_samples_train': len(y_train),
    'n_samples_test': len(y_test),
    'r2_train': regressor.score(X_train, y_train.drop('index', axis=1)),
    'r2_test': r2_score(y_test.drop('index', axis=1), Y_test_pred),
    'oob_score': regressor.oob_score_,
    'nse_test': nse,
    'pbias_test': pbias,
    'max_depth': params.get('max_depth'),
    'max_features': params.get('max_features'),
    'min_samples_leaf': params.get('min_samples_leaf'),
    'min_samples_split': params.get('min_samples_split'),
    'n_estimators': params.get('n_estimators'),
    'bootstrap': params.get('bootstrap')
}

# Create DataFrame from results and export to CSV
df_results = pd.DataFrame({'Attribute': results.keys(), f'{model.upper()}': results.values()})
df_results.to_csv(f'{model_dir}/{model}_results.csv', sep=',', index=False)

# Create DataFrame of feature importances and export to CSV
feature_importances = regressor.feature_importances_
feature_names = regressor.feature_names_in_
imp_df = pd.DataFrame({'feature': feature_names, 'importance': feature_importances})\
    .sort_values('importance', ascending=False)\
    .reset_index(drop=True)
imp_df.to_csv(f'{model_dir}/{model}_feature_importances.csv', sep=',', index=False)
