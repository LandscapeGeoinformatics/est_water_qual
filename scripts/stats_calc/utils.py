# Import libraries
import os
import pathlib

import geopandas as gpd
import numpy as np
from osgeo import gdal
from rasterstats import zonal_stats
import pandas as pd


# Get path to catchments
def fp_to_catchments():
    fp = None
    cwd = os.getcwd()
    filename = 'catchments.shp'
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/est_water_qual/data/catchments', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'est_water_qual/data/catchments', filename)
    return fp


# Load catchments
def load_catchments():
    fp = fp_to_catchments()
    catchments = gpd.read_file(fp)
    catchments = catchments.set_crs(3301, allow_override=True)
    return catchments


# Get catchment
def get_catchment(site_code):
    catchments = load_catchments()
    catchment = catchments[catchments['site_code'] == site_code].reset_index(drop=True)
    return catchment


# Get path to zones
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


# Get zone IDs
def get_zone_ids(site_code):
    catchment = get_catchment(site_code)
    zones = load_zones()
    zone_ids = gpd.sjoin(catchment, zones[['id', 'geometry']], how='left').reset_index(drop=True)['id'].to_list()
    return zone_ids


# Get LULC class value
def get_lulc_class_val(lulc_class):
    classes = ['arable', 'forest', 'grassland', 'other', 'urban', 'water', 'wetland']
    values = range(1, len(classes) + 1)
    class_dict = dict(zip(classes, values))
    return class_dict.get(lulc_class)


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


# Load streams
def load_streams(site_code):
    fp = fp_to_streams()
    catchment = get_catchment(site_code)
    streams = gpd.read_file(fp, mask=catchment)
    return streams


# Get path to riparian vegetation data
def fp_to_rip_veg_data():
    fp = None
    cwd = os.getcwd()
    filename = 'puhverriba_taimkate.gpkg'
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'Evelyn/veekaitsevoondid/final files/FINAL/export_archive', filename)
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


# Get path to predictor raster
def fp_to_predictor_raster(site_code, predictor):
    zone_ids = get_zone_ids(site_code)
    vrt_input = [fp_to_zonal_raster(predictor, zone_id) for zone_id in zone_ids]
    vrt = f'/vsimem/{site_code}_{predictor}.vrt'
    gdal.BuildVRT(vrt, vrt_input)
    fp = f'/vsimem/{site_code}_{predictor}.tif'
    gdal.Translate(fp, vrt, creationOptions=['COMPRESS=LZW', 'PREDICTOR=2'])
    return fp


# Get raster band number to read
def get_band_num(predictor, year):
    years = range(2016, 2021)
    band_num_dict = dict(zip(years, range(1, len(years) + 1)))
    if predictor in ['precip', 'snow_depth', 'temp_max', 'temp_mean', 'temp_min']:
        band_num = band_num_dict[year]
    else:
        band_num = 1
    return band_num


# Get list of zonal stats to calculate
def zonal_stats_to_calc(predictor):
    if predictor == 'temp_max':
        stats = ['max']
    elif predictor in ['precip', 'snow_depth', 'temp_mean']:
        stats = ['mean']
    elif predictor == 'temp_min':
        stats = ['min']
    else:
        stats = ['min', 'max', 'mean', 'std']
    return stats


# Create DataFrame of zonal stats
def zonal_stats_df(site_code, predictor):
    catchment = get_catchment(site_code)
    stats_dicts = []
    for year in range(2016, 2021):
        band_num = get_band_num(predictor, year)
        ds = gdal.Open(fp_to_predictor_raster(site_code, predictor))
        no_data = ds.GetRasterBand(band_num).GetNoDataValue()
        if no_data is None:
            no_data = np.nan
        stats_to_calc = zonal_stats_to_calc(predictor)
        prefix = f'{predictor}_'
        if predictor in ['temp_max', 'temp_mean', 'temp_min']:
            prefix = predictor.split('_')[0] + '_'
        stats = zonal_stats(
            catchment, fp_to_predictor_raster(site_code, predictor), band_num=band_num, nodata=no_data,
            stats=stats_to_calc, prefix=prefix
        )
        stats_dict = stats[0]
        stats_dict['year'] = year
        stats_dicts.append(stats_dict)
    stats_df = pd.DataFrame(stats_dicts)
    stats_df.insert(0, 'site_code', site_code)
    return stats_df


# Export stats to CSV
def export_stats(stats_df, predictor):
    cwd = os.getcwd()
    stats_dir = None
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        stats_dir = os.path.join(cwd, f'holgerv/est_water_qual/data/predictors/{predictor}')
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        stats_dir = os.path.join(cwd, f'est_water_qual/data/predictors/{predictor}')
    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)
    site_code = stats_df['site_code'].unique()[0]
    filename = f'{site_code}_{predictor}_stats.csv'
    fp = os.path.join(cwd, stats_dir, filename)
    stats_df.to_csv(fp, sep=',', index=False)
    return


# Get pollution sensitivity class value
def get_sen_class_val(sen_class):
    classes = ['vl', 'l', 'm', 'h', 'vh']
    values = range(1, len(classes) + 1)
    class_dict = dict(zip(classes, values))
    return class_dict.get(sen_class)


# Get path to livestock data
def fp_to_livestock_data():
    fp = None
    cwd = os.getcwd()
    filename = 'PRIA_famid.xlsx'
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/livestock', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'livestock', filename)
    return fp


# Calculate livestock units
def calc_livestock_units(cattle, sheep, goats, pigs):
    return cattle + sheep * 0.21 + goats * 0.21 + pigs * 0.2


# Get path to counties
def fp_to_counties():
    filename = 'maakond_20210901.shp'
    fp = None
    cwd = os.getcwd()
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/est_water_qual/data/maakond_shp', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'est_water_qual/data/maakond_shp', filename)
    return fp
