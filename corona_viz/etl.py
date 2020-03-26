import re
import datetime as dt
import pandas as pd
import numpy as np

from scipy.stats import linregress

from corona_viz.common import COVID_DATA_BASE, TRANSL, RAW_DATA_PATH

DF = pd.DataFrame

def load_data() -> DF:
    """Load confirmed, deaths and recovered and combine in single dataframe"""
    # %%
    conf = load_data_typ( "confirmed", date_fmt='%m/%d/%y' )
    recov = load_data_typ("recovered", date_fmt='%m/%d/%Y')
    death = load_data_typ("deaths", date_fmt='%m/%d/%y')
    # %%
    data = ( conf
             .merge( recov, on=['province', 'country', 'date'], how='left' )
             .merge( death, on=['province', 'country', 'date'], how='left' ) )
    # %%

    data['n_active'] = (data['n_confirmed']
                        - data['n_recovered'].fillna(0)
                        - data['n_deaths'].fillna(0) )

    # %%
    data1 = (data.groupby(['country', 'date']).sum().reset_index())
    # %%
    data2 = gen_projections( data1 )
    data2['pais'] = data2['country'].apply(lambda s: TRANSL.get(s, s))
    # %%
    return data2


def gen_projections( data: DF ) -> DF:
    """Generate projections following simple exponential model"""
    # %%
    past = data.copy()
    past['log_n_confirmed'] = np.log( past['n_confirmed'] + 1.1 )

    countries = data.loc[data['n_confirmed'] > 0, 'country'].value_counts()

    # ctry = "Colombia"
    # cnt = countries.loc[ctry]

    pieces = []
    for ctry, cnt in countries.items():
        if cnt < 8:
            continue
        pieces.append(calc_projection( past, ctry ) )

    proy_df_all = pd.concat( pieces )
    ret = pd.concat([past, proy_df_all]).sort_values(['country', 'date'])
    # %%
    return ret
    # %%


def load_data_typ( typ, date_fmt: str ):
    """Load time series data and reshape
    typ can be one of {confirmed, deaths, recovered}"""""
    # %%
    df = pd.read_csv( RAW_DATA_PATH / f"time_series_covid19_{typ}_global.csv" )
    date_cols = [ col for col in df.columns if re.match("[0-9]+/[0-9]+/[0-9]+", col ) ]
    id_cols = [ 'Province/State', 'Country/Region' ]
    for col in id_cols:
        df[col] = df[col].astype( 'category' )
    # %%
    for col in date_cols:
        df.loc[ df[col] == 0, col ] = np.nan
    # %
    value_name = f'n_{typ.lower()}'
    df2 = pd.melt(df, id_vars=id_cols, value_vars=date_cols,
                  var_name='date',
                  value_name=value_name)
    df2 = df2[ df2[value_name].notnull() ]
    df2['date'] = pd.to_datetime( df2['date'], format=date_fmt )
    df2.rename( columns={'Province/State': 'province',
                         'Country/Region': 'country'},
                inplace=True )

    return df2
    # %%


def max_raw_data_mtime():
    # %%
    return max( (RAW_DATA_PATH / f"time_series_covid19_{typ}_global.csv")
                .stat().st_mtime
                for typ in ['confirmed', 'deaths', 'recovered'])
    # %%


def calc_projection(past: DF, ctry: str):
    """Compute projections for a country"""
    # %
    df = past.loc[ (past['country'] == ctry) & (past['n_confirmed'] > 0),
                   ["date", "n_confirmed", "log_n_confirmed"] ].copy()
    max_date = df['date'].max()
    # %
    df['x'] = (df['date'] - max_date).dt.total_seconds() / (24.0 * 60.0 * 60.0)

    df = df[ df['x'] >= -7.0 ]
    # %
    slope, intercept, r_value, p_value, _ = linregress( df['x'], df['log_n_confirmed'] )
    # print( ctry, slope, intercept )
    # %
    proj_df = pd.DataFrame( {"country": ctry, "x": range(0, 10)})
    proj_df['date'] = max_date + proj_df['x'].apply( lambda x: dt.timedelta(x) )
    log_est = intercept + slope * proj_df['x']
    proj_df['n_confirmed_est'] = np.exp( log_est )
    # %
    return proj_df.drop(['x'], axis=1)
    # %%

def get_data_col():
    # %%
    import requests
    # %%
    rp = requests.get("https://e.infogram.com/01266038-4580-4cf0-baab-a532bd968d0c"
                      "?parent_url=https%3A%2F%2Fwww.ins.gov.co%2FNoticias%2FPaginas%2FCoronavirus.aspx&src=embed#")
    # %%
    print( rp.headers, rp.status_code)
    # %%
    with open(COVID_DATA_BASE + "/col_data.html", "w") as f_out:
        f_out.write( rp.text )


def interactive_testing():
    """Interctive testing"""
    # %%
    # noinspection PyUnresolvedReferences
    runfile('corona_viz/etl.py')
    # %%
    conf = load_data_typ('confirmed', date_fmt='%m/%d/%y')
    # %%
    recov = load_data_typ('recovered', date_fmt='%m/%d/%Y')
    # %%
    # conf_afg = conf[ conf.country == 'Afghanistan']
    # %%
    data = load_data()
    # %%
    # ctry = data[data.country == 'Italy']
    # %%
