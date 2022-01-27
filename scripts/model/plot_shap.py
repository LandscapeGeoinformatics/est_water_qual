# Import libraries
import sys
import os
from joblib import load

import pandas as pd
import shap
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.inspection import PartialDependenceDisplay

from utils import get_model_dir

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

# Create DataFrame of SHAP values and export to CSV
explainer = shap.TreeExplainer(regressor)
shap_values = shap.TreeExplainer(regressor).shap_values(X_test)
shap_df = pd.DataFrame(
    list(zip(X_test.columns, np.abs(shap_values).mean(0))), columns=['feature', 'abs_mean_shap']
)
shap_df = shap_df\
    .sort_values(by=['abs_mean_shap'], ascending=False)\
    .reset_index(drop=True)
shap_df.to_csv(f'{model_dir}/{model}_shap.csv', sep=',', index=False)

# Get indices of top 10 features
feature_names = shap_df.head(10)['feature'].to_list()
indices = []
for feat in feature_names:
    index = X_test.columns.to_list().index(feat)
    indices.append(index)

# Read results
results = pd.read_csv(f'{model_dir}/{model}_results.csv')

# Get R2 calculated on test data
r2_test = round(float(results[results['Attribute'] == 'r2_test'][f'{model.upper()}'].iloc[0]), 3)

# SHAP summary plot
shap.summary_plot(
    shap_values[:, indices], X_test.iloc[:, indices], plot_type='bar', feature_names=feature_names, show=False
)
fig = plt.gcf()
plt.title(f'{model.upper()}' + '\n' + '$\mathregular{R^{2}=}$' + f'{r2_test}')
plt.tight_layout()
plt.savefig(f'{model_dir}/{model}_shap_imp.png', dpi=300, bbox_inches='tight')
plt.close(fig)

# SHAP summary plot
shap.summary_plot(shap_values[:, indices], X_test.iloc[:, indices], feature_names=feature_names, show=False)
fig = plt.gcf()
plt.title(f'{model.upper()}' + '\n' + '$\mathregular{R^{2}=}$' + f'{r2_test}')
plt.tight_layout()
plt.savefig(f'{model_dir}/{model}_shap_summary.png', dpi=300, bbox_inches='tight')
plt.close(fig)

# Create partial dependence plot
fig, ax = plt.subplots(figsize=(12, 12))
disp = PartialDependenceDisplay.from_estimator(regressor, X_test, feature_names, ax=ax)
ax.set_title(f'{model.upper()}' + '\n' + '$\mathregular{R^{2}=}$' + f'{r2_test}')
plt.tight_layout()
plt.subplots_adjust(top=1.1)
plt.savefig(f'{model_dir}/{model}_pdp.png', dpi=300, bbox_inches='tight')
