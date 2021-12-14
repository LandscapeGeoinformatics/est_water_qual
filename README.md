# est_water_qual

Scripts and notebooks used for modeling nutrient concentrations in Estonian streams.

The **scripts** are divided into three folders. Folder **preprocessing** contains scripts used for preprocessing the predictor variables. Folder **stats_calc** contains scripts used for extracting statistics from the predictor variables that were used as features in the model. Folder **model** contains scripts related to the random forest (RF) model used for predicting total nitrogen (TN) and total phosphorus (TP) in streams.

**preprocessing** contains the following scripts:
* *preprocess_catchments.py* for preprocessing the catchments originating from the Estonian Nature Information System (EELIS)
* *preprocess_\*.py* for preprocessing source data (e.g. *preprocess_dem.py*) used as predictors in the model
* *preprocess_wq_obs.py* for preprocessing water quality data from the Estonian environment monitoring system (KESE)
* *utils.py* containing helper functions for loading and subsetting source data from corresponding raster and vector files

**stats_calc** contains the following scripts:
* *calc_area.py* for calculating catchment area
* *calc_\*_prop.py* for calculating proportion statistics for limestone, land use and land cover (LULC) and pollution sensitivity and vegetation in riparian buffers
* *calc_\*_prop_buff.py* for calculating proportion statistics in stream buffers
* *calc_livestock_density.py* for calculating livestock density within catchments
* *calc_manure_dep.py* for calculating nitrogen and phosphorus deposition in manure
* *calc_stats.py* as a generic script for extracting zonal statistics for climate, soil and topographic variables
* *calc_stream_density.py* for calculating stream density in catchments as the total length of streams divided by catchment area
* *concat_stats.py* for concatenating the derived statistics for each predictor
* *utils.py* containing helper functions for extracting statistics from predictor variables

**model** contains the following scripts:
* *extract_site_catchments.py* for extracting the catchments of observation sites used in the model
* *prepare_ml_input.py* for merging the predictor variables with the water quality observations
* *utils.py* containing helper functions used for building the model

Most of the Python scripts also have corresponding shell scripts that were used for submitting Slurm jobs to the HPC cluster of University of Tartu.

The **notebooks** folder contains the following Jupyter notebooks used for analyzing the water quality data:
* *explore_wq_data.ipynb* for statistics and plots about the water quality observations
