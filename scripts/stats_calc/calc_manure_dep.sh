#!/bin/bash

#SBATCH -p main
#SBATCH -J calc_manure_dep
#SBATCH -N 4
#SBATCH --ntasks-per-node=1
#SBATCH -t 00:30:00
#SBATCH --mem=64G
#SBATCH --array=0-68
#SBATCH -o /gpfs/space/home/holgerv/gis_holgerv/est_water_qual/scripts/log/slurm-%A_%a_%x.out

cd /gpfs/space/home/holgerv/gis_holgerv/est_water_qual

module purge
module load python-3.7.1

source activate water_qual_env

# Input variables
wd=/gpfs/rocket/samba/gis
site_codes=($(ogrinfo -ro -dialect sqlite -sql "SELECT kkr_kood FROM Hüdrokeemia_valglad" data/Valglad/Hüdrokeemia_valglad.shp | grep kkr_kood | awk -F= '{gsub(/ /,""); print $2}'))
predictor=$1

# Run script
~/.conda/envs/water_qual_env/bin/python scripts/stats_calc/calc_manure_dep.py ${wd} ${site_codes[$SLURM_ARRAY_TASK_ID]} ${predictor}
