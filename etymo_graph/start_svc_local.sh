set -x
source $HOME/venvs/py38-fintech

PYTHONPATH='etymo_graph'

uvicorn --reload svc:app
