#!/bin/bash

. "/home/ubuntu/miniconda3/etc/profile.d/conda.sh"
conda activate bokeh2
cd /home/ubuntu/scratch || exit
export PYTHONPATH=./
export COVID_DATA_BASE=/home/ubuntu/COVID-19
export COVID_PARQUETS_DIR=/home/ubuntu/_data/covid/
# nohup gunicorn --workers=2 --bind 0.0.0.0:8080 --access-logfile - 'corona_viz.app:create_app()'
nohup gunicorn --workers=5 --bind 0.0.0.0:8080 --reload --capture-output --error-logfile - \
   --access-logfile - 'corona_viz.app:create_app()' > cvv_srv.log 2>&1
