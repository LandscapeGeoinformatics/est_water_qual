# Import libraries
import os
import pathlib

import geopandas as gpd
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score

import shap

import seaborn as sns


# Get path to ML input
def fp_to_ml_input(param):
    fp = None
    cwd = os.getcwd()
    filename = f'{param}_ml_input.csv'
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/est_water_qual/model', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'est_water_qual/model', filename)
    return fp


# Get features used as predictors
def get_features(version):
    total_features = ['arable_prop', 'arable_prop_buff_100', 'arable_prop_buff_1000',
       'arable_prop_buff_500', 'awc1_min', 'awc1_max', 'awc1_mean', 'awc1_std',
       'bd1_min', 'bd1_max', 'bd1_mean', 'bd1_std', 'clay1_min', 'clay1_max',
       'clay1_mean', 'clay1_std', 'dem_min', 'dem_max', 'dem_mean', 'dem_std',
       'flowlength_min', 'flowlength_max', 'flowlength_mean', 'flowlength_std',
       'forest_disturb_prop_buff_100', 'forest_disturb_prop_buff_1000',
       'forest_disturb_prop_buff_500', 'forest_prop', 'grassland_prop',
       'k1_min', 'k1_max', 'k1_mean', 'k1_std', 'livestock_density',
       'maxtemp_max', 'meantemp_mean', 'mintemp_min', 'other_prop',
       'pol_sen_drain_pol_sen_h_prop', 'pol_sen_drain_pol_sen_m_prop',
       'pol_sen_drain_pol_sen_vh_prop', 'pol_sen_nat_pol_sen_h_prop',
       'pol_sen_nat_pol_sen_m_prop', 'pol_sen_nat_pol_sen_vh_prop',
       'precip_mean', 'rip_veg_drain_prop', 'rip_veg_nat_prop', 'rock1_min',
       'rock1_max', 'rock1_mean', 'rock1_std', 'sand1_min', 'sand1_max',
       'sand1_mean', 'sand1_std', 'silt1_min', 'silt1_max', 'silt1_mean',
       'silt1_std', 'slope_min', 'slope_max', 'slope_mean', 'slope_std',
       'snowdepth_mean', 'soc1_min', 'soc1_max', 'soc1_mean', 'soc1_std',
       'stream_density', 'tri_min', 'tri_max', 'tri_mean', 'tri_std',
       'twi_min', 'twi_max', 'twi_mean', 'twi_std', 'urban_prop', 'water_prop',
       'wetland_prop']
    features = []
    if version == 1:
        features = total_features
    elif version == 2:
        for feat in total_features:
            stat = feat.split('_')[-1]
            if stat not in ['max', 'min', 'std'] and 'temp_' not in feat:
                features.append(feat)
            elif 'temp_' in feat:
                features.append(feat)
    elif version == 3:
        for feat in total_features:
            stat = feat.split('_')[-1]
            if stat not in ['max', 'min', 'std'] and 'temp_' not in feat and 'pol_sen' not in feat and 'prop_buff' not in feat:
                features.append(feat)
            elif 'temp_' in feat:
                features.append(feat)
            elif 'pol_sen' in feat:
                if 'vh' in feat:
                    features.append(feat)
            elif 'prop_buff' in feat:
                if '1000' in feat:
                    features.append(feat)
    elif version == 4:
        for feat in total_features:
            stat = feat.split('_')[-1]
            if stat not in ['max', 'min', 'std'] and 'temp_' not in feat and 'pol_sen' not in feat and 'prop_buff' not in feat:
                features.append(feat)
            elif 'temp_' in feat:
                features.append(feat)
            elif 'pol_sen' in feat:
                if 'vh' in feat:
                    features.append(feat)
            elif 'prop_buff' in feat:
                if '1000' in feat:
                    features.append(feat)
        for feat in features:
            if feat in [
                'awc1_mean', 'tri_mean', 'twi_mean', 'soc1_mean', 'flowlength_mean', 'bd1_mean', 'k1_mean',
                'slope_mean'
            ]:
                features.remove(feat)
    return features


# Get path of output directory
def get_output_dir(version_name):
    cwd = os.getcwd()
    output_dir = None
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        output_dir = os.path.join(cwd, f'holgerv/est_water_qual/model/{version_name}')
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        output_dir = os.path.join(cwd, f'est_water_qual/model/{version_name}')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir
