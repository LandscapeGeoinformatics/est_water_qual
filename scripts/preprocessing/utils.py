# Import libraries
import pathlib
import os

import geopandas as gpd
import numpy as np


# Get path to processing zones
def fp_to_zones():
    fp = None
    cwd = os.getcwd()
    filename = 'DEM_1m_processing_zones.shp'
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'kmoch/grid_tiles', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'est_water_qual/data/grid_tiles', filename)
    return fp


# Load processing zones
def load_zones():
    fp = fp_to_zones()
    zones = gpd.read_file(fp)
    zones['id'] = zones['id'].astype(np.int16)
    zones = zones.set_crs(3301, allow_override=True)
    return zones


# Get processing zone
def get_zone(zone_id):
    zones = load_zones()
    zone = zones[zones['id'] == zone_id].reset_index(drop=True)
    return zone


# Get path to soil data
def fp_to_soil_data():
    filename = 'EstSoil-EH_v1.2c.gpkg'
    fp = None
    cwd = os.getcwd()
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'kmoch/estsoil-eh_soilmap', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'soil', filename)
    return fp


# Get path to DEM data
def fp_to_dem_data(zone_id):
    filename = f'zone_{zone_id}_dem_5m.vrt'
    fp = None
    cwd = os.getcwd()
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'Evelyn/est_topographic_metrics/DEM5', filename)
    return fp


# Get path to LULC data
def fp_to_lulc_data():
    filename = 'lulc_simplified_classified.gpkg'
    fp = None
    cwd = os.getcwd()
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'kmoch/estsoil-eh_soilmap', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'lulc', filename)
    return fp


# Get LULC class value
def get_lulc_class_val(lulc_class):
    classes = ['arable', 'forest', 'grassland', 'other', 'urban', 'water', 'wetland']
    values = range(1, len(classes) + 1)
    class_dict = dict(zip(classes, values))
    return class_dict.get(lulc_class)


# Get path to climate data
def fp_to_climate_data(predictor):
    filename = None
    if predictor in ['temp_max', 'temp_mean', 'temp_min']:
        filename = '2m_temperature.nc'
    elif predictor == 'precip':
        filename = 'total_precipitation.nc'
    elif predictor == 'snow_depth':
        filename = 'snow_depth.nc'
    fp = None
    cwd = os.getcwd()
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/era5', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'era5', filename)
    return fp


# Get path to forest disturbance data
def fp_to_forest_disturb_data():
    fp = None
    cwd = os.getcwd()
    filename = 'estonia/disturbance_year_1986-2020_estonia.tif'
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/forest_disturb', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'forest_disturb', filename)
    return fp


# Get intermediate path segment of predictor raster
def intermediate_fp_segment(predictor):
    fp_segment = None
    cwd = os.getcwd()
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        if predictor in ['arable', 'forest', 'grassland', 'other', 'urban', 'water', 'wetland']:
            fp_segment = 'holgerv/lulc'
        elif predictor in ['awc1', 'bd1', 'clay1', 'k1', 'rock1', 'sand1', 'silt1', 'soc1']:
            fp_segment = f'holgerv/soil/{predictor}'
        elif predictor in ['dem', 'forest_disturb']:
            fp_segment = f'holgerv/{predictor}'
        elif predictor in ['flowlength', 'slope']:
            fp_segment = 'kmoch/nomograph/soil_prep'
        elif predictor in ['precip', 'snow_depth', 'temp_max', 'temp_mean', 'temp_min']:
            fp_segment = f'holgerv/era5/{predictor}'
        elif predictor == 'tri':
            fp_segment = 'HannaIngrid/TRI_5m'
        elif predictor == 'twi':
            fp_segment = 'HannaIngrid/saga_TWI_5m/TWI'
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        if predictor in ['arable', 'forest', 'grassland', 'other', 'urban', 'water', 'wetland']:
            fp_segment = 'lulc'
        elif predictor in ['awc1', 'bd1', 'clay1', 'k1', 'rock1', 'sand1', 'silt1', 'soc1']:
            fp_segment = f'soil/{predictor}'
        elif predictor == 'forest_disturb':
            fp_segment = f'{predictor}'
        elif predictor in ['precip', 'snow_depth', 'temp_max', 'temp_mean', 'temp_min']:
            fp_segment = f'era5/{predictor}'
    return fp_segment


# Get path to zonal raster
def fp_to_zonal_raster(predictor, zone_id):
    cwd = os.getcwd()
    fp_segment = intermediate_fp_segment(predictor)
    zonal_raster_dir = os.path.join(cwd, fp_segment)
    if not os.path.exists(zonal_raster_dir):
        os.makedirs(zonal_raster_dir)
    filename = f'{predictor}_5m_pzone_{zone_id}.tif'
    if predictor in ['arable', 'forest', 'grassland', 'other', 'urban', 'water', 'wetland']:
        filename = f'lulc_5m_pzone_{zone_id}.tif'
    fp = os.path.join(zonal_raster_dir, filename)
    return fp


# Get path to manure data
def fp_to_manure_data(predictor):
    filename = f'{predictor}.csv'
    fp = None
    cwd = os.getcwd()
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/manure', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'manure', filename)
    return fp


# Get path to arable land data
def fp_to_arable_land_data():
    filename = f'arable_land.csv'
    fp = None
    cwd = os.getcwd()
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/manure', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'manure', filename)
    return fp


# Get path to streams
def fp_to_streams():
    fp = None
    cwd = os.getcwd()
    filename = 'eelis_streams.gpkg'
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/est_water_qual/data/eelis', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'est_water_qual/data/eelis', filename)
    return fp


# Get path to limestone data
def fp_to_limestone_data():
    filename = 'aluspohja lubjakivi.shp'
    fp = None
    cwd = os.getcwd()
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/Eesti kaardid/Aluspohi ja pinnakate', filename)
    return fp
