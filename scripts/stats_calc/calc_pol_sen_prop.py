# Import libraries
import numpy as np
import sys
import os

import geopandas as gpd
import pandas as pd

from utils import get_catchment, get_sen_class_val, export_stats

# Input arguments
wd = sys.argv[1]
site_code = sys.argv[2]
predictor = sys.argv[3]
sen_class = sys.argv[4]

# Change working directory
os.chdir(wd)

# Get catchment
catchment = get_catchment(site_code)

# Layer to read
layer = None

# Layer for vegetation in buffers of natural streams
if predictor == 'pol_sen_nat':
    layer = 'LVK_veekaitsevoondi_reostustundlikkus'
# Layer for vegetation in buffers of drainage ditches
elif predictor == 'pol_sen_drain':
    layer = 'MSR_veekaitsevoondi_reostustundlikkus'

# Read pollution sensitivity data
fp = os.path.join(
    os.getcwd(), 'Evelyn/veekaitsevoondid/final files/FINAL/export_archive/Veekaitsevoondi_reostustundlikkus.gpkg'
)
pol_sen = gpd.read_file(fp, mask=catchment, layer=layer)

# Clip data with catchment
pol_sen_clip = gpd.clip(pol_sen, catchment, keep_geom_type=True).reset_index(drop=True)

# Get pollution sensitivity class value
sen_class_val = get_sen_class_val(sen_class)

# Calculate proportion
prop = 0
if not pol_sen_clip.empty:
    pol_sen_clip['RT_klass'] = pol_sen_clip['RT_klass'].astype(np.int32)
    if sen_class_val in list(pol_sen_clip['RT_klass'].unique()):
        prop = pol_sen_clip[pol_sen_clip['RT_klass'] == sen_class_val].area.sum() / pol_sen_clip.area.sum()

# Create DataFrame of stats
years = range(2016, 2021)
stats = [prop for i in range(len(years))]
stats_df = pd.DataFrame(list(zip(stats, years)), columns=[f'{predictor}_pol_sen_{sen_class}_prop', 'year'])
stats_df.insert(0, 'site_code', site_code)

# Export stats to CSV
export_stats(stats_df, f'{predictor}_{sen_class}_prop')
