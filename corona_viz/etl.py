"""Routines for getting data from the outside world"""

from typing import Dict, List, Any
import re
import json
import datetime as dt

import pandas as pd
import numpy as np
import requests
import bs4
from scipy.stats import linregress

from corona_viz.common import TRANSL, RAW_DATA_PATH, PARQUET_PATH

DF = pd.DataFrame
# %%

def load_data_world() -> DF:
    """Load confirmed, deaths and recovered and combine in single dataframe"""
    # %%
    conf = load_data_typ( "confirmed", date_fmt='%m/%d/%y' )
    recov = load_data_typ("recovered", date_fmt='%m/%d/%y')
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
    """Max modification time for data files world level"""
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


from pprint import pprint

"https://www.lahaus.com/p/san-martin-apartamentos/medellin"
    # %%

def get_and_save_data_col():
    """Get Colombia data"""
    # %%
    # rp = requests.get("https://e.infogram.com/01266038-4580-4cf0-baab-a532bd968d0c",
    #                   headers={'Cache-Control': 'max-age=100000', 'Accept': 'text/csv'})
    # print( rp.headers )

    #  rp = requests.get( "https://coronaviruscolombia.gov.co/Covid19/index.html" )
    rp = requests.get( "https://e.infogram.com/api/live/flex/0e44ab71-9a20-43ab-89b3-0e73c594668f/832a1373-0724-4182-a188-b958f9bf0906?" )
    print(f"data_col: infogram reply: status: {rp.status_code} - {len(rp.text)} chars")

    json_tbl = json.loads( rp.text )["data"][0]
    # json_tbl = extract_json_tbl(rp.text)

    df = pd.DataFrame( json_tbl[1:], columns=json_tbl[0])
    # %%
    df.rename( columns={'ID de caso': 'id',
                        'Fecha de diagnóstico': 'confirmed_date',
                        'Ciudad de ubicación': 'city',
                        'Departamento': 'state',
                        'Atención': 'care',
                        'Edad': 'age',
                        'Sexo': 'sex',
                        'Tipo*': 'typ',
                        'País de procedencia': 'origin_ctry'}, inplace=True)
    df = df[ df['id'] != '' ]
    df['confirmed_date'] = pd.to_datetime( df['confirmed_date'], format="%d/%m/%Y" )
    df['confirmed_date'] = df['confirmed_date'].dt.date
    df['care'] = df['care'].str.lower()
    df['in_hospital'] = df['care'] == 'hospital'
    df['recovered'] = df['care'] == 'recuperado'
    df['death'] = df['care'] == 'fallecido'
    df['active'] = (~df['recovered']) & (~df['death'])

    max_date = df['confirmed_date'].max()
    fp = PARQUET_PATH / f'colombia/df_col_{max_date}.parquet'
    print( f"data_col: Writing {df.shape} to: {fp}")
    df.to_parquet( fp )

    # %%

def extract_json_tbl( resp_text: str ):
    doc = bs4.BeautifulSoup(resp_text, features='html.parser')  # , parser='html.parser')
    els = doc.findAll("script")
    print( f"data_col: {len(els)} script elems")
    # %
    data = None
    for el in els:
        if el.text.startswith("window.infographicData="):
            data_str = el.text[ len("window.infographicData="):-1]
            data = json.loads( data_str )
            break

    if data is None:
        print("No window.infoGraphicData script element found" )
        raise RuntimeError()
    # %
    try:
        tbl = data['elements']['content']['content']['entities'][
                   '41b1ef61-e7cf-42f4-ae4a-1f15477c22f5']['props']['chartData']['data'][0]
    except KeyError as err:
        print( "Failed getting data from json: "
               "data['elements']['content']['content']['entities'].keys() =",
               data['elements']['content']['content']['entities'].keys() )
        print( f"data_col: Will dump data to {PARQUET_PATH / 'data.json'}")
        dump_all_json( data )

        raise err

    return tbl
    # %%


def dump_all_json( data: Dict ):
    """Dump data json object to file"""
    fp_out = PARQUET_PATH / "colombia/data.json"
    print(fp_out)
    # %
    with open(fp_out, "w") as f_out:
        json.dump( data, indent=4, fp=f_out )


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
