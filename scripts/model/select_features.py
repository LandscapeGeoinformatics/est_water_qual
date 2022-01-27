# Import libraries
import sys
import os

import pandas as pd

from utils import get_model_dir, fp_to_ml_input

# Input arguments
wd = sys.argv[1]
feat_set = sys.argv[2]

# Change working directory
os.chdir(wd)

# Model directory
param = feat_set.split('_')[0]
version = feat_set.split('_')[2]
model = f'{param}_model_{version}'
model_dir = get_model_dir(model)

# Read ML input
param = feat_set.split('_')[0]
ml_input = pd.read_csv(fp_to_ml_input(param), sep=',')

# Extract columns with features and replace missing values with mode
X = ml_input.iloc[:, 4:]
y = ml_input['obs_value']
X[X.columns] = X[X.columns].fillna(X.mode().iloc[0])

# Get features to keep
to_keep = pd.read_csv(f'{model_dir}/{feat_set}_to_keep.csv')['feature'].to_list()

# Reduce the number of features
X_reduced = X[to_keep]

# Create ML input and export to CSV
df = pd.concat([ml_input.iloc[:, :4], X_reduced], axis=1)
df.to_csv(f'{model_dir}/{feat_set}_ml_input.csv', sep=',', index=False)
