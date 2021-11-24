# Import libraries
import sys
import os

import geopandas as gpd
import pandas as pd

from utils import get_catchment, fp_to_livestock_data, calc_livestock_units, export_stats

# Input arguments
wd = sys.argv[1]
site_code = sys.argv[2]
predictor = 'livestock_density'

# Change working directory
os.chdir(wd)

# Get catchment
catchment = get_catchment(site_code)

# Read livestock data
fp = fp_to_livestock_data()
df = pd.concat([pd.read_excel(fp, sheet_name=sheet_name) for sheet_name in pd.ExcelFile(fp).sheet_names])

# Fill empty cells with 0
for col in df.columns[-4:]:
    df[col] = df[col].fillna(0)

# Create GeoDataFrame of points
points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['Y - koordinaat'], df['X- koordinaat']), crs=3301)

# Join catchment with points
catchment_with_points = gpd.sjoin(catchment, points, how='left').reset_index(drop=True)

# Calculate livestock units
catchment_with_points['livestock_units'] = catchment_with_points\
    .apply(
        lambda x: calc_livestock_units(
            x['Veised seisuga 31.12.2020'],
            x['Lambad seisuga 31.12.2020'],
            x['Kitsed seisuga 31.12.2020'],
            x['Sead seisuga 31.12.2020']
        ), axis=1
    )

# Calculate livestock units per hectare in catchment
livestock_density = catchment_with_points['livestock_units'].sum() / (catchment.area.sum() / 10000)

# Create DataFrame of stats
years = range(2016, 2021)
stats = [livestock_density for i in range(len(years))]
stats_df = pd.DataFrame(list(zip(stats, years)), columns=[f'{predictor}', 'year'])
stats_df.insert(0, 'site_code', site_code)

# Export stats to CSV
export_stats(stats_df, f'{predictor}')
