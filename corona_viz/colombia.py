"""Routines for generating info for colombia page"""

from typing import Dict
from importlib import reload

import pandas as pd
import corona_viz.common as com
from corona_viz.common import Date, DataCacheRec, PARQUET_PATH

DF = pd.DataFrame

DATA_CACHE: Dict[Date, DataCacheRec] = {}
# %%

def get_htmls() -> Dict:
    """Load process, adapt to html"""
    data_rec = load_col_data()
    # print( data_rec.dtype )
    data_dic = summarize_col_data( data_rec )
    htmls = render_html( data_dic )

    return htmls


def load_col_data() -> DataCacheRec:
    """Load data from local parquet that should have been created by independent process
    running gen_parquet.py"""
    # %%
    reload( com )
    data_rec = com.get_data(DATA_CACHE,
                            glob_str=str(PARQUET_PATH / "colombia/df_col_*.parquet"),
                            date_col='confirmed_date')
    df = data_rec.data
    df['death'] = df['death'].astype(int)
    # %%
    return data_rec


def summarize_col_data( data_rec: DataCacheRec ) -> Dict:
    """Process the case by case data frame to produce summaries"""
    # %%
    df = data_rec.data
    df['confirmed'] = 1

    by_sex = df['sex'].value_counts()
    # %%
    agg_spec = {
        'confirmed': 'count',
        'death': 'sum',
        'recovered': 'sum',
        'active': 'sum'
    }

    by_city = ( df
                .groupby('city').agg(agg_spec).reset_index()
                .sort_values('confirmed', ascending=False) )
    by_state = ( df.groupby('state').agg(agg_spec).reset_index()
                 .sort_values('confirmed', ascending=False) )

    by_sex_age_agg = ( df
                       .groupby( ['age', 'sex'] )
                       .agg( {'confirmed': 'count'} )
                       .reset_index() )

    by_sex_age = ( by_sex_age_agg
                   .pivot(index='age', columns='sex', values='confirmed')
                   .reset_index() )

    by_sex_age.index.name = None
    by_sex_age.columns.name = None

    # %%
    data = {"confirmed": df['confirmed'].sum(),
            "deaths": df['death'].sum(),
            "active": df['active'].sum(),
            "recovered": df['recovered'].sum(),
            "in_hospital": df['in_hospital'].sum(),
            "men": by_sex.loc['M'],
            "women": by_sex.loc['F'],
            "n_cities": by_city.shape[0],
            "n_states": by_state.shape[0],
            "by_city": by_city,
            "by_state": by_state,
            "by_sex_age": by_sex_age,
            "last_mtime": data_rec.mtime
            }
    # %%
    return data
    # %%


def render_html( data: Dict ):
    """Return a dict of things that can be inserted directly in the html template"""
    # %
    htmls = data.copy()

    col_renames = {
        'state': 'Departamento',
        'confirmed': 'Confirmados',
        'death': 'Muertes',
        'recovered': 'Recuperados',
        'sex': 'Sexo',
        'age': 'Edad',
        'M': 'Hombres',
        'F': 'Mujeres',
        'active': 'Activos',
        'city': 'Municipio'
    }

    for key in ['by_city', 'by_state', 'by_sex_age']:
        htmls[key] = ( data[key]
                       .rename( columns=col_renames )
                       .to_html(na_rep='-', index=False, float_format='%.0f') )

    htmls['last_mtime'] = com.tstamp_to_dt( data['last_mtime'] ).isoformat(sep=' ')[:-10] + ' UTC'

    return htmls
    # %%
