# Import libraries
import sys
import os
from joblib import load

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from utils import get_model_dir, fp_to_area_stats

sns.set_theme()

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

# Read results
results = pd.read_csv(f'{model_dir}/{model}_results.csv')
obs_vs_pred = pd.read_csv(f'{model_dir}/{model}_obs_vs_pred.csv', sep=',')

# Get R2 calculated on test data
r2_test = round(float(results[results['Attribute'] == 'r2_test'][f'{model.upper()}'].iloc[0]), 3)

# Plot observed and predicted values
fig, ax = plt.subplots(1, 1)
sns.scatterplot(data=obs_vs_pred, x='obs_value', y='pred_value')
plt.title(f'{model.upper()}' + '\n' + '$\mathregular{R^{2}=}$' + f'{r2_test}')
plt.tight_layout()
plt.savefig(f'{model_dir}/{model}_obs_vs_pred.png', dpi=300, bbox_inches='tight')

# Plot observed values and ratios
fig, ax = plt.subplots(1, 1)
sns.scatterplot(data=obs_vs_pred, x='obs_value', y='ratio')
plt.title(f'{model.upper()}' + '\n' + '$\mathregular{R^{2}=}$' + f'{r2_test}')
plt.tight_layout()
plt.savefig(f'{model_dir}/{model}_obs_vs_ratio.png', dpi=300, bbox_inches='tight')

# Plot predicted values and ratios
fig, ax = plt.subplots(1, 1)
sns.scatterplot(data=obs_vs_pred, x='pred_value', y='ratio')
plt.title(f'{model.upper()}' + '\n' + '$\mathregular{R^{2}=}$' + f'{r2_test}')
plt.tight_layout()
plt.savefig(f'{model_dir}/{model}_pred_vs_ratio.png', dpi=300, bbox_inches='tight')

# Plot observed values and residuals
fig, ax = plt.subplots(1, 1)
sns.scatterplot(data=obs_vs_pred, x='obs_value', y='residual')
plt.title(f'{model.upper()}' + '\n' + '$\mathregular{R^{2}=}$' + f'{r2_test}')
plt.tight_layout()
plt.savefig(f'{model_dir}/{model}_obs_vs_res.png', dpi=300, bbox_inches='tight')

# Plot predicted values and residuals
fig, ax = plt.subplots(1, 1)
sns.scatterplot(data=obs_vs_pred, x='pred_value', y='residual')
plt.title(f'{model.upper()}' + '\n' + '$\mathregular{R^{2}=}$' + f'{r2_test}')
plt.tight_layout()
plt.savefig(f'{model_dir}/{model}_pred_vs_res.png', dpi=300, bbox_inches='tight')

# Plot histogram of predicted values
fig, ax = plt.subplots(1, 1)
sns.histplot(obs_vs_pred, x='pred_value', bins=20, multiple='stack', palette='Set1', legend=True, ax=ax)
ax.set_title(param.upper(), fontsize=12)
plt.title(f'{model.upper()}' + '\n' + '$\mathregular{R^{2}=}$' + f'{r2_test}')
plt.tight_layout()
plt.savefig(f'{model_dir}/{model}_pred_hist.png', dpi=300, bbox_inches='tight')

# Plot catchment areas and residuals
area_stats = pd.read_csv(fp_to_area_stats())
area_stats_grouped = area_stats.groupby('site_code')['area'].mean().reset_index()
area_vs_pred = obs_vs_pred.merge(area_stats_grouped, on='site_code')
fig, ax = plt.subplots(1, 1)
sns.scatterplot(data=area_vs_pred, x='area', y='residual')
plt.title(f'{model.upper()}' + '\n' + '$\mathregular{R^{2}=}$' + f'{r2_test}')
plt.tight_layout()
plt.savefig(f'{model_dir}/{model}_area_vs_res.png', dpi=300, bbox_inches='tight')

# Plot catchment areas and ratios
fig, ax = plt.subplots(1, 1)
sns.scatterplot(data=area_vs_pred, x='area', y='ratio')
plt.title(f'{model.upper()}' + '\n' + '$\mathregular{R^{2}=}$' + f'{r2_test}')
plt.tight_layout()
plt.savefig(f'{model_dir}/{model}_area_vs_ratio.png', dpi=300, bbox_inches='tight')
