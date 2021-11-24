#!/bin/bash

#SBATCH -p main
#SBATCH -J preprocess_lulc
#SBATCH -N 4
#SBATCH --ntasks-per-node=1
#SBATCH -t 01:00:00
#SBATCH --mem=64G
#SBATCH --array=1-22
#SBATCH -o /gpfs/space/home/holgerv/gis_holgerv/est_water_qual/scripts/log/slurm-%A_%a_%x.out

cd /gpfs/space/home/holgerv/gis_holgerv/est_water_qual

module purge
module load python-3.7.1

source activate water_qual_env

# Input variables
wd=/gpfs/rocket/samba/gis
zone_id=$SLURM_ARRAY_TASK_ID

# Run script
~/.conda/envs/water_qual_env/bin/python scripts/preprocessing/preprocess_lulc.py ${wd} ${zone_id}
