. "/home/teo/miniconda3/etc/profile.d/conda.sh"

conda activate bokeh2
export PYTHONPATH=./

gunicorn -w 2 'corona_viz.app:create_app()' --access-logfile -
