"""Routines for getting data from the outside world"""

from typing import Dict
import re
import json
import datetime as dt

import pandas as pd
import numpy as np
import requests
import bs4
# from scipy.stats import linregress
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression

from corona_viz.common import TRANSL, RAW_DATA_PATH, PARQUET_PATH

DF = pd.DataFrame
Ser = pd.Series
Array = np.ndarray
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
    data0 = data.groupby(['country', 'date']).sum().reset_index()
    data_world = data.groupby('date').sum().reset_index()
    data_world['country'] = 'World'

    data1 = pd.concat([data0, data_world])
    # %%
    data2 = gen_projections( data1, future_window=15 )
    data2['pais'] = data2['country'].apply(lambda s: TRANSL.get(s, s))
    # %%
    return data2


def gen_projections( data1: DF, future_window: int ) -> DF:
    """Generate projections following simple exponential model"""
    # %%
    past = data1.copy()
    past['log_n_confirmed'] = np.log( past['n_confirmed'] + 1.1 )

    countries = data1.loc[data1['n_confirmed'] > 0, 'country'].value_counts()

    # ctry = "Colombia"
    # cnt = countries.loc[ctry]
    time_window = 10.0
    pieces = []
    # %%
    for ctry, cnt in countries.items():
        if cnt < (time_window + 1):
            continue

        print( ctry )
        pieces.append(calc_projection_logistic(past, ctry, time_window=time_window,
                                               future_window=future_window))

    proy_df_all = pd.concat( pieces )
    ret = pd.concat([past, proy_df_all]).sort_values(['country', 'date'])
    # %%
    return ret
    # %%


def load_data_typ( typ, date_fmt: str ):
    """Load time series data and reshape
    typ can be one of {confirmed, deaths, recovered}"""
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
    """Compute projections for a country using simple exponential"""
    # %
    df = past.loc[ (past['country'] == ctry) & (past['n_confirmed'] > 0),
                   ["date", "n_confirmed", "log_n_confirmed"] ].copy()
    max_date = df['date'].max()
    # %
    df['x'] = (df['date'] - max_date).dt.total_seconds() / (24.0 * 60.0 * 60.0)
    df['x2'] = df['x'] * df['x'] / 50

    df = df[ df['x'] >= -7.0 ]
    # %
    lr = LinearRegression()
    reg_cols = ['x']  # ['x', 'x2']
    lr.fit( X=df[reg_cols], y=df['log_n_confirmed'] )
    # slope, intercept, r_value, p_value, _ =
    # print( ctry, slope, intercept )
    # %
    proj_df = pd.DataFrame( {"country": ctry, "x": range(0, 10)})
    proj_df['date'] = max_date + proj_df['x'].apply( lambda x: dt.timedelta(x) )
    proj_df['x2'] = proj_df['x'] * proj_df['x'] / 50
    log_est = lr.predict( proj_df[reg_cols] )
    proj_df['n_confirmed_est'] = np.exp( log_est )
    # %
    return proj_df.drop(['x'], axis=1)
    # %%


def calc_projection_logistic(past: DF, ctry: str, time_window: float, future_window: int):
    """Compute projections for a country using logistic growth model"""
    # %%
    df = ( past.loc[(past['country'] == ctry) & (past['n_confirmed'] > 0),
                    ["date", "n_confirmed", "log_n_confirmed"] ]
           .sort_values('date').copy() )
    max_date = df['date'].max()
    # %
    df['x'] = (df['date'] - max_date).dt.total_seconds() / (24.0 * 60.0 * 60.0)
    # df['sigma'] = 0.01

    df = df[ df['x'] >= -time_window ]
    # %
    x = df['x']
    y = df['log_n_confirmed']

    # %%
    popt = fit_to_curve(x, y )
    # %%
    proj_df = extrapolate( ctry, max_date, future_window, popt )
    # %%
    return proj_df


def extrapolate( ctry: str, max_date, future_window: int, popt: Array ) -> DF:
    """extrapolate to the near future using exponential or logistic growth model"""
    # %%
    proj_df = pd.DataFrame( {"country": ctry, "x": range(0, future_window)})
    proj_df['date'] = max_date + proj_df['x'].apply( lambda x_: dt.timedelta(x_) )
    if len(popt) == 2:
        print( f"{ctry:20s} exp" )
        proj_df['n_confirmed_est'] = np.exp(exp_curve(proj_df['x'], popt[0], popt[1]))
    else:
        print( f"{ctry:20s} logistic {np.round(popt, 3)}" )
        proj_df['n_confirmed_est'] = np.exp(logistic(proj_df['x'], popt[0], popt[1], popt[2]))
    # %%
    return proj_df.drop(['x'], axis=1)
    # %%


def fit_to_curve( x: Ser, y: Ser ):
    """Fit to a logistic curve and if it fails, to a simple exponential"""
    # %
    y1 = y.shift( 1, fill_value=y.iloc[0] )
    y2 = y.shift(-1, fill_value=y.iloc[-1])
    ym = (y1 + y2) / 2.0 + 0.01
    # noinspection PyTypeChecker
    sigma = np.abs( ym - y )
    # sigma.iloc[-1] = 0.001
    # %
    try:
        # %
        m0 = y.mean() + 5
        k0 = max( 0, y.iloc[-1] - y.iloc[-2] )

        popt, _ = curve_fit( logistic, x, y, p0=[m0, k0, 0.0], sigma=sigma,
                             bounds=([0, 0, -np.inf], [np.inf, np.inf, np.inf]),
                             max_nfev=100)
        # adjust so that curve exactly matches y[-1] at x[-1]
        popt[0] += y.iloc[-1] - logistic(x.iloc[-1], popt[0], popt[1], popt[2] )
        # %
        return popt
    except RuntimeError as err:
        if err.args[0].find('maximum number of function evaluations') == -1:
            raise err
    # %
    m0 = y.iloc[-1]
    b0 = (y.iloc[-1] - y.iloc[-7]) / 6.0
    # adjust so that curve exactly matches y[-1] at x[-1]
    popt, _ = curve_fit( exp_curve, x, y, p0=[m0, b0], sigma=sigma)
    popt[0] += y.iloc[-1] - exp_curve(x.iloc[-1], popt[0], popt[1])
    # %
    return popt
    # %%


def logistic(x: Ser, m: float, k: float, c: float):
    """log( logistic(x; m, k, c) ) where
     logistic( x; m, k, c) = m / ( 1 + exp (- k * (x-c) ) """
    # noinspection PyTypeChecker
    return m - np.log( 1.0 + np.exp( -k * (x - c) ) )


# noinspection PyTypeChecker
def exp_curve(x: Ser, m: float, b: float ):
    """Exponential of linear function"""
    return m + b * x
    # %%


def get_and_save_data_col_v2():
    """Getting data as json directly from datos abiertos .gov.co"""
    # %%
    rp = requests.get( "https://www.datos.gov.co/api/views/gt2j-8ykr/rows.json?accessType=DOWNLOAD")
    # %%
    today = dt.date.today()

    with open( PARQUET_PATH / f"colombia/corona_viz_col_{today.isoformat()}.json", "wt") as f_out:
        f_out.write( rp.text )

    # %%
    json_obj = json.loads( rp.text )
    cols = [ rec['name'] for rec in json_obj['meta']['view']['columns'] ]

    df = pd.DataFrame( json_obj['data'], columns=cols )
    # %%
    renames = {'ID de caso': 'id_case',
               'Fecha diagnostico': 'confirmed_date',
               'Ciudad de ubicación': 'city',
               'Departamento o Distrito ': 'state',
               'atención': 'care',
               'Edad': 'age',
               'Sexo': 'sex',
               'Tipo': 'typ',
               'País de procedencia': 'origin_ctry'}

    for col in renames.keys():
        assert col in df.columns, f"{col} is missing from downloaded df: {df.columns}"

    df.rename(columns=renames, inplace=True)
    # %%
    # df['confirmed_date'] = df[ 'confirmed_date'].apply( fix_date )

    post_proc( df )
    # %%

def get_from_local_csv():
    # %%
    df = pd.read_csv('/home/teo/Downloads/Casos_positivos_de_COVID-19_en_Colombia.csv',
                     low_memory=False)
    # %%
    renames = {'ID de caso': 'id_case',
               'Fecha diagnostico': 'confirmed_date',
               'Fecha recuperado': 'recovery_date',
               'Fecha de muerte': 'death_date',
               'Ciudad de ubicación': 'city',
               'Departamento o Distrito ': 'state',
               'Estado': 'status',
               'atención': 'care',
               'Edad': 'age',
               'Sexo': 'sex',
               'Tipo': 'typ',
               'País de procedencia': 'origin_ctry'}
    # %%
    df1 = df.rename( columns=renames )
    # %%
    df1.death_date.value_counts().sort_index()
    # %%
    df1[df1.city == 'Medellín'].confirmed_date.value_counts().sort_index().tail(10)
    # %%
    df1[df1.state == 'Antioquia'].confirmed_date.value_counts().sort_index().tail(10)
    # %%


def get_and_save_data_col_v1():
    """Get Colombia data"""
    # %%
    # rp = requests.get("https://e.infogram.com/01266038-4580-4cf0-baab-a532bd968d0c",
    #                   headers={'Cache-Control': 'max-age=100000', 'Accept': 'text/csv'})
    # print( rp.headers )

    #  rp = requests.get( "https://coronaviruscolombia.gov.co/Covid19/index.html" )
    rp = requests.get( "https://e.infogram.com/api/live/flex/0e44ab71-9a20-43ab-89b3-0e73c594668f/"
                       "832a1373-0724-4182-a188-b958f9bf0906?" )

    print(f"data_col: gatos gov reply: status: {rp.status_code} - {len(rp.text)} chars")
    # %%

    json_tbl = json.loads( rp.text )["data"][0]
    # json_tbl = extract_json_tbl(rp.text)

    df = pd.DataFrame( json_tbl[1:], columns=json_tbl[0])
    # %%
    renames = {'ID de caso': 'id',
               'Fecha de diagnóstico': 'confirmed_date',
               'Ciudad de ubicación': 'city',
               'Departamento o Distrito': 'state',
               'Atención**': 'care',
               'Edad': 'age',
               'Sexo': 'sex',
               'Tipo*': 'typ',
               'País de procedencia': 'origin_ctry'}
    for col in renames.keys():
        assert col in df.columns, f"{col} is missing from downloaded df: {df.columns}"

    df.rename( columns=renames, inplace=True)
    # %%


def post_proc( df: DF ):
    """some massaging of the colombia data"""
    # %%
    df = df[ df['id'] != '' ]
    # df['confirmed_date'] = pd.to_datetime( df['confirmed_date'], format="%d/%m/%Y" )
    df['dconfirmed_date'] = pd.to_datetime( df['confirmed_date'] )
    # %%
    ser = df[ 'confirmed_date' ]
    # %%

    df['confirmed_date'] = df['confirmed_date'].dt.date
    # %%

    # %%
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


def fixed_date_col( ser: Ser ):
    """"""
    # %%
    ser1 = ser.where( ser.str.strip() != 'Sin dato', None )
    # %%


def extract_json_tbl( resp_text: str ):
    """No longer used..."""
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
    data = load_data_world()
    # %%
    # ctry = data[data.country == 'Italy']
    # %%
    return conf, data, recov


# %%
def fix_date( a_str: str ) -> str:
    """legacy: fix d/m/20 to d/m/2020"""
    ps = a_str.split('/')
    if len(ps) != 3:
        raise ValueError( f"bad date: {a_str}" )
    if ps[2] == '20':
        ps[2] = '2020'

    if ps[0] == '00':
        ps[0] = '01'

    return "/".join(ps)
# %%

def _interactive_testing():
    # %%
    runfile('corona_viz/etl.py')
    # %%