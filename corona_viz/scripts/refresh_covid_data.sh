#!/bin/bash

cd /home/ubuntu/COVID-19 || exit 1
NOW=$(date '+%Y%m%d %H%M')
(printf "\n\n%s" "$NOW"; git pull) >> /home/ubuntu/scratch/refresh.log 2>&1

. "/home/ubuntu/miniconda3/etc/profile.d/conda.sh"
conda activate bokeh2
cd /home/ubuntu/scratch || exit
export PYTHONPATH=./
export COVID_DATA_BASE=/home/ubuntu/COVID-19

python corona_viz/gen_parquet.py >> /home/ubuntu/scratch/refresh.log 2>&1
