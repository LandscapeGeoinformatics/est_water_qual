# Import libraries
import sys
import os

import pandas as pd

from utils import fp_to_manure_data, fp_to_arable_land_data

# Input arguments
wd = sys.argv[1]
predictor = sys.argv[2]

# Change working directory
os.chdir(wd)

# Read manure data
manure = pd.read_csv(fp_to_manure_data(predictor), sep=',', header=1, encoding='utf-8-sig')\
    .pipe(
        lambda df: df.rename(
            columns={df.columns[0]: 'year', df.columns[1]: 'county', df.columns[2]: f'{predictor}_t'}
        )
    )

# Read arable land data
arable_land = pd.read_csv(fp_to_arable_land_data(), sep=',', header=1)

# Melt arable land data
arable_land_melt = pd.melt(arable_land, id_vars=['Maakond'], value_vars=arable_land.columns[-5:])\
    .pipe(lambda df: df.assign(year=df['variable'].str.split().str[0].astype(int)))\
    .drop('variable', axis=1)\
    .rename(columns={'Maakond': 'county', 'value': 'arable_land_ha'})

# Merge counties with manure
manure_arable = manure.merge(arable_land_melt, how='left', on=['county', 'year'])

# Calculate amount of nutrient in kg per ha
manure_arable[f'{predictor}_kg_per_ha'] = (manure_arable[f'{predictor}_t'] * 1000) / manure_arable['arable_land_ha']
fp = os.path.join(os.path.dirname(fp_to_manure_data(predictor)), f'{predictor}_kg_per_ha.csv')
manure_arable.drop([f'{predictor}_t', 'arable_land_ha'], axis=1)\
    .to_csv(fp, sep=',', index=False, encoding='utf-8-sig')
