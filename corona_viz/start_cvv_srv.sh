#!/bin/bash

# need to activate bokeh2 first
# conda activate bokeh2
cd /home/ubuntu/scratch || exit
export PYTHONPATH=./
export COVID_DATA_BASE=/home/ubuntu/COVID-19
# nohup gunicorn --workers=2 --bind 0.0.0.0:8080 --access-logfile - 'corona_viz.app:create_app()'
nohup gunicorn --workers=2 --bind 0.0.0.0:8080 --capture-output --error-logfile - --access-logfile - 'corona_viz.app:create_app()' > cvv_srv.log 2>&1
