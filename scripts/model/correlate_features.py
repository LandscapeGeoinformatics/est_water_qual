# Import libraries
import sys
import os
from pathlib import Path

import pandas as pd
import numpy as np

from utils import fp_to_ml_input, get_model_dir, get_feat_group, fp_to_feature_groups

# Input arguments
wd = sys.argv[1]
param = sys.argv[2]

# Change working directory
os.chdir(wd)

# Read ML input
ml_input = pd.read_csv(fp_to_ml_input(param), sep=',')

# Extract columns with features and replace missing values with mode
X = ml_input.iloc[:, 4:]
y = ml_input['obs_value']
X[X.columns] = X[X.columns].fillna(X.mode().iloc[0])

# Calculate correlation between the features
feat_corr = pd.DataFrame(X.corr().abs().unstack().sort_values(kind='quicksort', ascending=False).reset_index())
feat_corr = feat_corr\
    .rename(
        columns={
            feat_corr.columns[0]: 'feature_1',
            feat_corr.columns[1]: 'feature_2',
            feat_corr.columns[2]: 'feat_corr'
        }
    )
feat_corr = feat_corr[feat_corr['feature_1'] != feat_corr['feature_2']].reset_index(drop=True)
feat_corr = feat_corr.iloc[::2].reset_index(drop=True)

# Calculate correlation between the features and target
target_corr = X.corrwith(y).abs().to_frame().reset_index()
target_corr = target_corr\
    .rename(columns={target_corr.columns[0]: 'feature', target_corr.columns[1]: 'target_corr'})\
    .sort_values('target_corr', ascending=False)\
    .reset_index(drop=True)

# Merge DataFrames
corr_merged = feat_corr.copy()
corr_merged = corr_merged\
    .merge(
        target_corr.rename(columns={'feature': 'feature_1', 'target_corr': 'feature_1_target_corr'}), on='feature_1'
    )
corr_merged = corr_merged\
    .merge(
        target_corr.rename(columns={'feature': 'feature_2', 'target_corr': 'feature_2_target_corr'}), on='feature_2'
    )

# Add column showing the feature that has a lower correlation with the target
corr_merged['lower_target_corr'] = np.where(
    corr_merged['feature_1_target_corr'] > corr_merged['feature_2_target_corr'],
    corr_merged['feature_2'], corr_merged['feature_1']
)
corr_merged = corr_merged.sort_values('feat_corr', ascending=False).reset_index(drop=True)
corr_merged.to_csv(os.path.join(Path(fp_to_feature_groups()).parent.absolute(), f'{param}_corr.csv'), index=False)

# Thresholds
thresholds = [0.9, 0.8, 0.7, 0.6]

# Iterate over thresholds and export features to drop and keep to CSV
for threshold, version in zip(thresholds, range(1, len(thresholds) + 1)):

    # Feature set
    feat_set = f'{param}_feat_v{version}'

    # Model directory
    model = f'{param}_model_v{version}'
    model_dir = get_model_dir(model)

    # Get feature dictionary
    feature_groups = pd.read_csv(fp_to_feature_groups())
    feat_dict = dict(zip(feature_groups['feature'], feature_groups['group']))

    # Extract features with correlation values above threshold
    df = corr_merged[corr_merged['feat_corr'] > threshold].reset_index(drop=True)

    # Extract features to drop
    to_drop = []
    for feat in df['lower_target_corr'].to_list():
        group = get_feat_group(feat)
        if list(feat_dict.values()).count(group) > 1:
            if feat not in to_drop and feat in feat_dict.keys():
                del feat_dict[feat]
                to_drop.append(feat)

    # Export features to keep to CSV
    target_corr[target_corr['feature'].isin(to_drop)].reset_index(drop=True) \
        .to_csv(f'{model_dir}/{feat_set}_to_drop.csv', index=False)

    # Export features to drop to CSV
    target_corr[~target_corr['feature'].isin(to_drop)].reset_index(drop=True) \
        .to_csv(f'{model_dir}/{feat_set}_to_keep.csv', index=False)
