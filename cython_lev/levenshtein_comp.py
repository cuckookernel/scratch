
import sys
import time
from importlib import reload
from typing import Optional

import pandas as pd
import pyximport

pyximport.install(reload_support=True)

from Levenshtein import distance

from shared.common_ext_imports import DF
from shared.db_util import DbUtil

sys.path.append('shared/examples/cython_lev/')
import levenshtein_dist as ld

CASES = [
    ('mateo', 'pateo', 1),
    ('mateo', 'matio', 1),
    ('mateo', 'matea', 1),
    ('mateo', 'pablo', 3),
]
# %%


def _interactive_testing():
    # %%
    runpyfile('shared/examples/cython_lev/levenshtein_comp.py')
    df = _get_random_data()
    # %%


def test_few_cases():
    for case in CASES:
        start, target, expected = case
        my_ver = ld.levenshtein_dist_mat_v1( start, target )
        lev = distance( start, target )
        computed = print( f"{start} {target}: {my_ver} {expected} {lev}" )


def _get_random_data() -> DF:
    # %%
    dbut = DbUtil('snowflake')
    # tables = dbut.read_sql( 'show tables in ML_SANDBOX' )
    # %%
    condos = dbut.read_sql(' select distinct name from LISTINGS_RC')
    unit_condo_name = dbut.read_sql("""select distinct condo_name
                                       from STAGING.EXT__SOBREPLANOS__REAL_ESTATES
                                       where condo_name is not null and condo_name != ''""")

    n_samples = 100000
    units_sample = ( unit_condo_name['condo_name'].sample(n=n_samples, replace=True)
                     .reset_index(drop=True) )
    condos_sample = ( condos['name'].sample( n=n_samples, replace=True )
                      .reset_index(drop=True) )
    # %%
    df = pd.DataFrame( {'s1': units_sample, 's2': condos_sample} )

    return df


def _random_test( df: Optional[DF] = None ):
    if df is None:
        df = _get_random_data()
    # %%
    # # A true test!
    df1 = df.iloc[:1000]
    dist_lev = df1.apply( lambda row: distance( row['s1'], row['s2'] ), axis=1 )
    dist_mat = df1.apply( lambda row: ld.levenshtein_dist_vec_v0(row['s1'], row['s2']),
                          axis=1 )

    res_df = pd.DataFrame( dict( dist_lev=dist_lev,
                                 dist_mat=dist_mat,
                                 diff=dist_lev != dist_mat,
                                 s1_shorter=df1['s1'].str.len() < df1['s2'].str.len()) )

    assert ((dist_lev - dist_mat) == 0).all()
    # %%


def _performance_benchmark( df: DF ):
    # %%
    reload( ld )
    df1 = df.iloc[:10000].copy()
    n = len(df1)

    for fun in [ distance, ld.levenshtein_dist_vec_v0]:  # , ld.levenshtein_dist_vec_v0]:

        t0 = time.process_time()
        df1['dist'] = df1.apply(lambda row: fun(row['s1'], row['s2']), axis=1)
        t1 = time.process_time()
        print(f'n ={n} Elapsed {fun.__name__}: {t1 - t0}')

    # %%
