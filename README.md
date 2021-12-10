# est_water_qual

Scripts used for modeling nutrient concentrations in Estonian streams.

The scripts are divided into three folders. Folder **preprocessing** contains scripts used for preprocessing the predictor variables. Folder **stats_calc** contains scripts used for extracting statistics from the predictor variables that were used as features in the model. Folder **model** contains scripts related to the random forest (RF) model used for predicting total nitrogen (TN) and total phosphorus (TP) in streams.

**preprocessing** contains the following scripts:
* *utils.py* containing helper functions for loading and subsetting source data from corresponding raster and vector files
* *preprocess_\** for preprocessing source data (e.g.*preprocess_dem.py*) used as predictors in the model
* *preprocess_catchments* for preprocessing the catchments originating from the Estonian Nature Information System (EELIS)
* *preprocess_wq_obs* for preprocessing water quality data from the Estonian environment monitoring system (KESE)

**stats_calc** contains the following scripts:
* *utils.py* containing helper functions for extracting statistics from predictor variables
* *calc_area* for calculating catchment area
* *calc_\*_prop* for calculating proportion statistics for limestone, land use and land cover (LULC) and pollution sensitivity and vegetation in riparian buffers
* *calc_\*_prop_buff* for calculating proportion statistics in stream buffers
* *calc_livestock_density* for calculating livestock density within catchments
* *calc_manure_dep* for calculating nitrogen and phosphorus deposition in manure
* *calc_stats* as a generic script for extracting zonal statistics for climate, soil and topographic variables
* *calc_stream_density* for calculating stream density in catchments as the total length of streams divided by catchment area
* *concat_stats* for concatenating the derived statistics for each predictor

Most of the Python scripts also have corresponding shell scripts that were used for submitting Slurm jobs to the HPC cluster of University of Tartu.
