#!/bin/bash

LOG_FILE=/home/ubuntu/scratch/covid_refresh.log

cd /home/ubuntu/COVID-19 || exit 1
NOW=$(date '+%Y-%m-%d %H:%M UTC')
(printf "\n\n%s\n" "$NOW"; git pull) >> "$LOG_FILE" 2>&1

. "/home/ubuntu/miniconda3/etc/profile.d/conda.sh"
conda activate bokeh2
cd /home/ubuntu/scratch || exit
export PYTHONPATH=./
export COVID_DATA_BASE=/home/ubuntu/COVID-19
export COVID_PARQUETS_DIR=/home/ubuntu/_data/covid

python corona_viz/gen_parquet.py >>  "$LOG_FILE" 2>&1
