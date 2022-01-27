# Import libraries
import os

import pandas as pd

from utils import fp_to_ml_input, get_feat_dict

# Input arguments
wd = 'D:/'
param = 'tn'

# Change working directory
os.chdir(wd)

# Read ML input
ml_input = pd.read_csv(fp_to_ml_input(param), sep=',')

# Extract columns with features
X = ml_input.iloc[:, 4:]
y = ml_input['obs_value']

# Get feature dictionary
feat_dict = get_feat_dict(X.columns)

# Create DataFrame and export to CSV
df = pd.DataFrame(feat_dict.items(), columns=['feature', 'group'])
df.to_csv('est_water_qual/model/feature_groups.csv', index=False)
