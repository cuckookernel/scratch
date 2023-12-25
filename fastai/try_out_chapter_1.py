
from fastai import *
from fastai.collab import *
from fastai.data import *
from fastai.data.external import *

# %%

def main():
    # %%
    path = untar_data(URLs.ML_SAMPLE)
    # %%
    print( path )
    # %%
    dls = CollabDataLoaders.from_csv(path / 'ratings.csv')
    # %%
    learn = collab_learner(dls, use_nn=False, layers=[50,10], y_range=(0.5, 5.5))
    learn.fine_tune(50)
    # %%
