#!/bin/bash

# need to activate bokeh2 first
# conda activate bokeh2
cd /home/ubuntu/scratch || exit
export PYTHONPATH=./
export COVID_DATA_BASE=/home/ubuntu/COVID-19
gunicorn --workers=2 'corona_viz.app:create_app()'
