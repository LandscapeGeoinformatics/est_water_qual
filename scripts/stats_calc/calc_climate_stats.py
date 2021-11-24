# Import libraries
import sys
import os
import utils
from osgeo import gdal

# Input variables
working_dir = sys.argv[1]
site_code = sys.argv[2]
predictor = sys.argv[3]

# Set working directory
os.chdir(working_dir)

# # Load catchments
# catchments = utils.load_catchments('holgerv/est_water_qual/data/Valglad/Hüdrokeemia_valglad.shp')
#
# # Get catchment
# catchment = utils.get_catchment(catchments, site_code)
#
# # Load zones
# zones = utils.load_zones('kmoch/grid_tiles/DEM_1m_processing_zones.shp')

# Get zone IDs
zone_ids = utils.get_zone_ids(site_code)

# Get VRT input
vrt_input = [f'holgerv/era5/{predictor}/{predictor}_5m_pzone_{zone_id}.tif' for zone_id in zone_ids]

# Create VRT from zonal raster files
predictor_vrt = f'/vsimem/{site_code}_{predictor}.tif'
gdal.BuildVRT(predictor_vrt, vrt_input)

# Create predictor raster and clip by catchment
# gdal.Warp(
#     predictor_raster, vrt, dstNodata=None, cutlineDSName='holgerv/est_water_qual/data/Valglad/Hüdrokeemia_valglad.shp',
#     cutlineWhere=f"kkr_kood='{site_code}'", cropToCutline=True
# )
# gdal.Warp(
#     predictor_raster, vrt, dstNodata=None, cutlineDSName=utils.fp_to_catchments(),
#     cutlineWhere=f"kkr_kood='{site_code}'", cropToCutline=True
# )

# # Get annual stats
# ds = gdal.Open(predictor_raster)
# stats = []
# for i, year in zip(range(1, 6), range(2016, 2021)):
#     band = None
#     if ds.RasterCount == 5:
#         band = ds.GetRasterBand(i)
#     else:
#         band = ds.GetRasterBand(1)
#     array = band.ReadAsArray()
#     stats_dict = {'year': year}
#     if predictor == 'maxtemp':
#         stats_dict[f'{predictor}_max'] = array.max()
#     elif predictor == 'mintemp':
#         stats_dict[f'{predictor}_min'] = array.min()
#     elif predictor in ['meantemp', 'precip', 'snowdepth']:
#         stats_dict[f'{predictor}_mean'] = array.mean()
#         # stats_dict[f'{predictor}_mean'] = np.nanmean(array)
#     else:
#         stats_dict[f'{predictor}_min'] = array.min()
#         stats_dict[f'{predictor}_max'] = array.max()
#         stats_dict[f'{predictor}_mean'] = array.mean()
#         stats_dict[f'{predictor}_std'] = array.std()
#     stats.append(stats_dict)
# ds = None

# Create DataFrame of zonal stats
stats_df = utils.zonal_stats_df(site_code, predictor, predictor_vrt)

# # Create DataFrame from stats
# stats_df = pd.DataFrame(stats)
# stats_df.insert(0, 'site_code', site_code)

# Export to CSV
output_dir = os.path.join(f'holgerv/est_water_qual/data/predictors/{predictor}')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
stats_csv = os.path.join(output_dir, f'{site_code}_{predictor}_stats.csv')
stats_df.to_csv(stats_csv, sep=',', index=False)
