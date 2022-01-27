# Import libraries
import sys
import os
from joblib import dump

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor

from utils import get_model_dir

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
ml_input = pd.read_csv(f'{model_dir}/{feat_set}_ml_input.csv', sep=',')

# Extract features and target
X = ml_input.iloc[:, 4:]
y = ml_input['obs_value']

# Split the data into training and test sets
test_size = 0.3
random_state = 1
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

# Export training and test data to CSV
X_train.to_csv(f'{model_dir}/{feat_set}_feat_train.csv', index_label='index')
X_test.to_csv(f'{model_dir}/{feat_set}_feat_test.csv', index_label='index')
y_train.to_csv(f'{model_dir}/{feat_set}_target_train.csv', index_label='index')
y_test.to_csv(f'{model_dir}/{feat_set}_target_test.csv', index_label='index')

# Parameters and their distributions for RandomizedSearchCV

# Number of trees in random forest
n_estimators = list(np.linspace(start=10, stop=100, num=10, dtype=int))
# Number of features to consider at every split
max_features = ['auto', 'sqrt', 'log2']
# Maximum number of levels in tree
max_depth = list(np.linspace(start=10, stop=100, num=10, dtype=int))
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]
# Create dictionary from parameters
param_distributions = {
    'n_estimators': n_estimators,
    'max_features': max_features,
    'max_depth': max_depth,
    'min_samples_split': min_samples_split,
    'min_samples_leaf': min_samples_leaf,
    'bootstrap': bootstrap
}

# Perform search for hyperparameters
estimator = RandomForestRegressor()
rf_random = RandomizedSearchCV(
    estimator=estimator, param_distributions=param_distributions, n_iter=100, verbose=2, random_state=random_state,
    n_jobs=-1
)

# Get best parameters
rf_random.fit(X_train, y_train)
params = rf_random.best_params_
params['bootstrap'] = True
params['oob_score'] = True

# Fit parameters to the model
regressor = RandomForestRegressor()
regressor.set_params(**params)
regressor.fit(X_train, y_train)

# Save model
dump(regressor, f'{model_dir}/{model}.joblib')
