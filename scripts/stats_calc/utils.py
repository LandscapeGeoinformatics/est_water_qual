# Import libraries
import os
import pathlib

import geopandas as gpd
import numpy as np
from osgeo import gdal
from rasterstats import zonal_stats
import pandas as pd
import pylandstats as pls


# Get path to catchments
def fp_to_catchments():
    fp = None
    cwd = os.getcwd()
    filename = 'Hüdrokeemia_valglad.shp'
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        fp = os.path.join(cwd, 'holgerv/est_water_qual/data/Valglad', filename)
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        fp = os.path.join(cwd, 'est_water_qual/data/Valglad', filename)
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
    catchment = catchments[catchments['kkr_kood'] == site_code].reset_index(drop=True)
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


# Get intermediate path segment of predictor raster
def intermediate_fp_segment(predictor):
    fp_segment = None
    cwd = os.getcwd()
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        if predictor in ['maxtemp', 'meantemp', 'mintemp', 'precip', 'snowdepth']:
            fp_segment = f'holgerv/era5/{predictor}'
        elif predictor in ['awc1', 'bd1', 'clay1', 'k1', 'rock1', 'sand1', 'silt1', 'soc1']:
            fp_segment = f'holgerv/soil/{predictor}'
        elif predictor == 'dem':
            fp_segment = f'holgerv/{predictor}'
        elif predictor in ['flowlength', 'slope']:
            fp_segment = 'kmoch/nomograph/soil_prep'
        elif predictor == 'tri':
            fp_segment = 'HannaIngrid/TRI_5m'
        elif predictor == 'twi':
            fp_segment = 'HannaIngrid/saga_TWI_5m/TWI'
        # elif predictor in get_lulc_classes() or predictor == 'lulc' or 'arable_prop' in predictor:
        #     fp_segment = 'holgerv/lulc'
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        if predictor in ['maxtemp', 'meantemp', 'mintemp', 'precip', 'snowdepth']:
            fp_segment = f'era5/{predictor}'
        elif predictor in ['awc1', 'bd1', 'clay1', 'k1', 'rock1', 'sand1', 'silt1', 'soc1']:
            fp_segment = f'soil/{predictor}'
        # elif predictor in get_lulc_classes() or predictor == 'lulc' or 'arable_prop' in predictor:
        #     fp_segment = 'lulc'
    return fp_segment


# Get path to zonal raster
def fp_to_zonal_raster(predictor, zone_id):
    cwd = os.getcwd()
    fp_segment = intermediate_fp_segment(predictor)
    zonal_raster_dir = os.path.join(cwd, fp_segment)
    if not os.path.exists(zonal_raster_dir):
        os.makedirs(zonal_raster_dir)
    filename = f'{predictor}_5m_pzone_{zone_id}.tif'
    # if predictor in get_lulc_classes() or predictor == 'lulc' or 'arable_prop' in predictor:
    #     filename = f'lulc_5m_pzone_{zone_id}.tif'
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
    band_num_dict = dict(zip(range(2016, 2021), range(1, 6)))
    if predictor in ['maxtemp', 'meantemp', 'mintemp', 'precip', 'snowdepth']:
        band_num = band_num_dict[year]
    else:
        band_num = 1
    return band_num


# Get list of zonal stats to calculate
def zonal_stats_to_calc(predictor):
    if predictor == 'maxtemp':
        stats = ['max']
    elif predictor in ['meantemp', 'precip', 'snowdepth']:
        stats = ['mean']
    elif predictor == 'mintemp':
        stats = ['min']
    else:
        stats = ['min', 'max', 'mean', 'std']
    return stats


# Create DataFrame of zonal stats
def zonal_stats_df(site_code, predictor):
    catchment = get_catchment(site_code)
    predictor_raster = fp_to_predictor_raster(site_code, predictor)
    stats_dicts = []
    for year in range(2016, 2021):
        band_num = get_band_num(predictor, year)
        ds = gdal.Open(predictor_raster)
        no_data = ds.GetRasterBand(band_num).GetNoDataValue()
        if no_data is None:
            no_data = np.nan
        stats_to_calc = zonal_stats_to_calc(predictor)
        stats = zonal_stats(
            catchment, predictor_raster, band_num=band_num, nodata=no_data, stats=stats_to_calc,
            prefix=f'{predictor}_'
        )
        stats_dict = stats[0]
        stats_dict['year'] = year
        stats_dicts.append(stats_dict)
    stats_df = pd.DataFrame(stats_dicts)
    stats_df.insert(0, 'site_code', site_code)
    return stats_df


# Calculate and export zonal stats to CSV
def export_zonal_stats(site_code, predictor):
    stats_df = zonal_stats_df(site_code, predictor)
    cwd = os.getcwd()
    stats_dir = None
    if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
        stats_dir = os.path.join(cwd, f'holgerv/est_water_qual/data/predictors/{predictor}')
    elif pathlib.Path(cwd) == pathlib.Path('D:/'):
        stats_dir = os.path.join(cwd, f'est_water_qual/data/predictors/{predictor}')
    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)
    filename = f'{site_code}_{predictor}_stats.csv'
    fp = os.path.join(cwd, stats_dir, filename)
    stats_df.to_csv(fp, sep=',', index=False)
    return


# # Export stats to CSV
# def export_stats(stats_df, site_code, predictor):
#     cwd = os.getcwd()
#     stats_dir = None
#     if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
#         stats_dir = os.path.join(cwd, f'holgerv/est_water_qual/data/predictors/{predictor}')
#     elif pathlib.Path(cwd) == pathlib.Path('D:/'):
#         stats_dir = os.path.join(cwd, f'est_water_qual/data/predictors/{predictor}')
#     if not os.path.exists(stats_dir):
#         os.makedirs(stats_dir)
#     filename = f'{site_code}_{predictor}_stats.csv'
#     fp = os.path.join(cwd, stats_dir, filename)
#     stats_df.to_csv(fp, sep=',', index=False)
#     return
#
#
# # Get path to streams
# def fp_to_streams():
#     fp = None
#     cwd = os.getcwd()
#     filename = 'eelis_streams.gpkg'
#     if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
#         fp = os.path.join(cwd, 'holgerv/est_water_qual/data/eelis', filename)
#     elif pathlib.Path(cwd) == pathlib.Path('D:/'):
#         fp = os.path.join(cwd, 'est_water_qual/data/eelis', filename)
#     return fp
#
#
# # Load streams
# def load_streams(site_code):
#     fp = fp_to_streams()
#     catchment = get_catchment(site_code)
#     streams = gpd.read_file(fp, mask=catchment)
#     return streams
#
#
# # Clip streams with catchment
# def clip_streams(site_code):
#     streams = load_streams(site_code)
#     catchment = get_catchment(site_code)
#     # streams_clip = gpd.clip(streams, catchment, keep_geom_type=True).reset_index(drop=True)
#     streams_clip = gpd.clip(streams, catchment).reset_index(drop=True)
#     return streams_clip
#
#
# # Buffer streams
# def buffer_streams(site_code, buff_dist):
#     streams_clip = clip_streams(site_code)
#     buffers = streams_clip.copy()
#     buffers['geometry'] = buffers.buffer(buff_dist)
#     # buffers = gpd.GeoDataFrame(geometry=streams_clip.buffer(buff_dist), crs=streams_clip.crs)
#     print(buffers.head())
#     return buffers
#
#
# # Get path to buffers
# def fp_to_buffers(site_code, buff_dist, predictor):
#     buffers = buffer_streams(site_code, buff_dist)
#     fp = f'/vsimem/{site_code}_{predictor}_buff.gpkg'
#     buffers.to_file(fp)
#     return fp
#
#
# # Get path to catchment raster
# def fp_to_catch_raster(site_code, predictor):
#     fp = f'/vsimem/{site_code}_{predictor}_catch.tif'
#     gdal.Warp(
#         fp, fp_to_predictor_raster(site_code, predictor), cutlineDSName=fp_to_catchments(),
#         cutlineWhere=f"kkr_kood='{site_code}'", cropToCutline=True
#     )
#     return fp
#
#
# # Get path to buffer raster
# def fp_to_buff_raster(site_code, predictor, buff_dist):
#     fp = f'/vsimem/{site_code}_{predictor}_buff.tif'
#     gdal.Warp(
#         fp, fp_to_predictor_raster(site_code, predictor),
#         cutlineDSName=fp_to_buffers(site_code, buff_dist, predictor), cropToCutline=True
#     )
#     return fp
#
#
# # Get landscape instance
# def get_landscape(filename):
#     ls = pls.Landscape(filename)
#     return ls
#
#
# # Calculate area of class in landscape
# def calc_class_area(landscape, class_val):
#     area = landscape.area(class_val).sum()
#     return area
#
#
# # Get path to LULC data
# def fp_to_lulc_data():
#     filename = 'lulc_simplified_classified.gpkg'
#     fp = None
#     cwd = os.getcwd()
#     if pathlib.Path(cwd) in [pathlib.Path('/gpfs/rocket/samba/gis'), pathlib.Path(r'\\ces.hpc.ut.ee\gis')]:
#         fp = os.path.join(cwd, 'kmoch/estsoil-eh_soilmap', filename)
#     elif pathlib.Path(cwd) == pathlib.Path('D:/'):
#         fp = os.path.join(cwd, 'lulc', filename)
#     return fp
#
#
# # Get LULC classes
# def get_lulc_classes():
#     lulc_classes = ['arable', 'forest', 'grassland', 'other', 'urban', 'water', 'wetland']
#     return lulc_classes


# def create_catchment_raster(site_code, predictor):
#     catchment = get_catchment(site_code)
#     fp_to_catchment = f'/vsimem/{site_code}_catchment.gpkg'
#     catchment.to_file(fp_to_catchment)
#     predictor_raster = create_predictor_raster(site_code, predictor)
#     catchment_raster = f'/vsimem/{site_code}_{predictor}.tif'
#     gdal.Warp(
#         catchment_raster, predictor_raster, cutlineDSName=fp_to_catchment, cropToCutline=True,
#         creationOptions=['COMPRESS=LZW', 'PREDICTOR=2'], dstNodata=np.nan
#     )
#     return catchment_raster
#
#
# def calc_stats(site_code, predictor):
#     catchment_raster = create_catchment_raster(site_code, predictor)
#     ds = gdal.Open(catchment_raster)
#     array = ds.GetRasterBand(1).ReadAsArray()
#     stats_dict = {
#         f'{predictor}_min': array[~np.isnan(array)].min(),
#         f'{predictor}_max': array[~np.isnan(array)].max(),
#         f'{predictor}_mean': array[~np.isnan(array)].mean(),
#         f'{predictor}_std': array[~np.isnan(array)].std()
#     }
#     print(stats_dict)
#     return
