#!/bin/bash

LOG_FILE=/home/ubuntu/scratch/corona_viz/refresh.log

cd /home/ubuntu/COVID-19 || exit 1
NOW=$(date '+%Y%m%d %H%M')
(printf "\n\n%s" "$NOW"; git pull) >> "$LOG_FILE" 2>&1

. "/home/ubuntu/miniconda3/etc/profile.d/conda.sh"
conda activate bokeh2
cd /home/ubuntu/scratch || exit
export PYTHONPATH=./
export COVID_DATA_BASE=/home/ubuntu/COVID-19

python corona_viz/gen_parquet.py >>  "$LOG_FILE" 2>&1
