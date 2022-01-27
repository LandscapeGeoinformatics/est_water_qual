# Import libraries
import os
import pathlib


# Get path to ML input
def fp_to_ml_input(param: str) -> str:
    fp = None
    cwd = os.getcwd()
    filename = f'{param}_ml_input.csv'
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\export.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/est_water_qual/model', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'est_water_qual/model', filename)
    return fp


# Get feature group
def get_feat_group(feat: str) -> str:
    if 'density' in feat:
        group = feat
    elif 'manure_dep' in feat:
        group = '_'.join(feat.split('_')[:2])
    elif 'pol_sen' in feat:
        group = '_'.join(feat.split('_')[:2])
    elif 'prop_buff' in feat:
        group = '_'.join(feat.split('_')[:-3])
    elif 'rip_veg' in feat:
        group = '_'.join(feat.split('_')[:2])
    elif feat == 'snow_depth_mean':
        group = '_'.join(feat.split('_')[:2])
    else:
        group = feat.split('_')[0]
    return group


# Get feature dictionary
def get_feat_dict(features: list) -> dict:
    feat_dict = {}
    for feat in features:
        group = get_feat_group(feat)
        feat_dict[feat] = group
    return feat_dict


# Get path to feature groups
def fp_to_feature_groups():
    fp = None
    cwd = os.getcwd()
    filename = 'feature_groups.csv'
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\export.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/est_water_qual/model', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'est_water_qual/model', filename)
    return fp


# Get path to area stats
def fp_to_area_stats():
    fp = None
    cwd = os.getcwd()
    filename = 'area_stats.csv'
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\export.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/est_water_qual/data/predictors/area', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'est_water_qual/data/predictors/area', filename)
    return fp


# Get path of model directory
def get_model_dir(model_name: str) -> str:
    cwd = os.getcwd()
    model_dir = None
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\export.hpc.ut.ee\gis')]:
        model_dir = os.path.join(cwd, f'holgerv/est_water_qual/model/{model_name}')
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        model_dir = os.path.join(cwd, f'est_water_qual/model/{model_name}')
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    return model_dir
