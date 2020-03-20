"""Generate nice interactive visualization of coronavirus time series"""
# %%
from typing import List
from pathlib import Path
import pandas as pd
import re
import numpy as np
import datetime as dt
import json
import os

from bokeh.io import output_file, show
from bokeh.palettes import Category10
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.embed import json_item


DF = pd.DataFrame
Date = dt.date
# %%

COVID_DATA_BASE = os.getenv('COVID_DATA_BASE', "/home/teo/git/COVID-19")
DATA_PATH = Path(f"{COVID_DATA_BASE}/csse_covid_19_data/csse_covid_19_time_series")
OUTPUT_DIR = Path("/home/teo/_data")

COUNTRIES = [ "Colombia", "Mexico", "Brazil", "Venezuela",
              "Italy", "Spain", "US",  "Germany"]

ACTIVE_COUNTRIES = { "Colombia", "Mexico", "Spain" }

TRANSL = {"Mexico": "México",
          "Italy": "Italia",
          "Spain": "España",
          "US": "EE.UU.",
          "Brazil": "Brasil",
          "Germany": "Alemania",
          "France": "Francia",
          "confirmed": "confirmados",
          "recovered": "recuperados",
          "deaths": "muertes",
          "active": "activos" }

TRANSL_INV = { v: k for k, v in TRANSL.items() }

DATA_CACHE = {}  # date -> DF
# %%
# TODO: use multi_line for estimate
# TODO: add referer to link


def interactive_testing():
    """Interctive testing"""
    # %%
    # noinspection PyUnresolvedReferences
    runfile('plots.py')
    # %%
    data = load_data()
    # %%
    ctry = data[data.country == 'Italy']
    # %%
    typ = "confirmed"
    plot = make_plot(data, klass="confirmed", scale="log")
    show(plot)
    # %%


def get_plot( klass: str, scale: str = "linear", date: Date = None,
              x_tools: List[str] = None, x_countries: List[str] = None ) -> str:

    """Return plot as json"""
    data = get_data( date )
    plot = make_plot(data, klass, scale, x_tools=x_tools, x_countries=x_countries)

    ret = json.dumps(json_item(plot, "klass"))

    return ret


def get_data(date: Date) -> DF:
    """Get DF for the given date"""
    if date is None:
        date = dt.date.today()

    if date in DATA_CACHE:
        print(f"retrieving data from memory cache: {date}")
    else:
        fp = OUTPUT_DIR / f"df_{date}.parquet"
        if os.path.exists( fp ):
            data = pd.read_parquet(fp)
            data['date'] = pd.to_datetime(data['date'])
        else:
            data = load_data()
            data_out = data.copy()

            data_out['date'] = data_out['date'].astype(str)
            data_out.to_parquet(fp)

        DATA_CACHE[date] = data

    return DATA_CACHE[date]


def make_plot(data: DF, klass: str, scale: str = "linear",
              x_tools: List[str] = None, x_countries: List[str] = None ):
    """Make a bokeh plot of a certain type (confirmed/recovered/deaths/active)
    scale can be "linear" or "log"
     for a bunch of countries"""
    x_tools = [] if x_tools is None else x_tools
    tools = x_tools + "crosshair reset hover previewsave".split()  # pan,box_zoom

    x_countries = [] if x_countries is None else x_countries
    countries = x_countries + [ c for c in COUNTRIES if c not in x_countries ]
    countries = countries[:10]

    y_axis_type = "log" if scale == "log" else "linear"

    p = figure(plot_width=800, plot_height=600, x_axis_type="datetime",
               y_axis_type=y_axis_type, tools=tools)
    # p.title.text = f'Corona virus by country - {klass.upper()} cases'
    p.xaxis.axis_label = "Fecha"
    p.yaxis.axis_label = ( "Número de Casos"
                           + " (escala logarítmica)" if y_axis_type == "log" else "" )

    for country, color in zip(countries, Category10[10]):
        df = data[data['country'] == country].copy()

        source = ColumnDataSource( data=dict( date=df['date'],
                                              date_str=df['date'].astype(str).str[:10],
                                              pais=df['pais'],
                                              n=df[f'n_{klass}'] ) )
        p.line('date', 'n',
               source=source,
               line_width=4, color=color, alpha=0.8,
               legend_label=TRANSL.get(country, country),
               visible=country in (ACTIVE_COUNTRIES.union(x_countries)))
        # p.circle(df['date'], df[f'n_{klass}'], color=color, legend_label=country)

    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = dict([
        # ("index", "$index"),
        # ("(xx,yy)", "(@x, @y)"),
        ( "País", "@pais"),
        ("Fecha", "@date_str"),
        (f"Total {TRANSL[klass]}", "@n"),
    ])

    # output_file(OUTPUT_DIR / f"{klass}.html", title=f"Cases by country - {klass}")
    return p
    # %%


def load_data() -> DF:
    """Load confirmed, deaths and recovered and combine in single dataframe"""
    conf = load_data_typ( "Confirmed" )
    print( conf.shape )
    recov = load_data_typ("Recovered")
    print( recov.shape)
    death = load_data_typ("Deaths")
    print( death.shape)
    # %%
    data = ( conf
             .merge( recov, on=['province', 'country', 'date'], how='left' )
             .merge( death, on=['province', 'country', 'date'], how='left' ) )

    data['n_active'] = (data['n_confirmed']
                        - data['n_recovered'].fillna(0)
                        - data['n_deaths'].fillna(0) )

    data = (data.groupby(['country', 'date']).sum().reset_index())
    data['pais'] = data['country'].apply(lambda s: TRANSL.get(s, s))

    # %%
    return data


def load_data_typ( typ='Confirmed' ):
    """Load time series data and reshape
    typ can be Confirmed, Deaths, Recovered"""""
    # %
    df = pd.read_csv( DATA_PATH / f"time_series_19-covid-{typ}.csv" )
    date_cols = [ col for col in df.columns if re.match("[0-9]+/[0-9]+/[0-9]+", col ) ]
    id_cols = [ 'Province/State', 'Country/Region' ]
    for col in id_cols:
        df[col] = df[col].astype( 'category' )
    # %
    for col in date_cols:
        df.loc[ df[col] == 0, col ] = np.nan
    # %
    value_name = f'n_{typ.lower()}'
    df2 = pd.melt(df, id_vars=id_cols, value_vars=date_cols,
                  var_name='date',
                  value_name=value_name)
    df2 = df2[ df2[value_name].notnull() ]
    df2['date'] = pd.to_datetime( df2['date'], format='%m/%d/%y' )
    df2.rename( columns={'Province/State': 'province',
                         'Country/Region': 'country'},
                inplace=True )

    return df2
    # %%


def old_version():
    """Simple proof of concept"""
    c_virus = pd.read_csv( "/home/teo/_data/time_series_19-covid-Confirmed.csv")
    # %%
    date_cols = [ col for col in c_virus.columns if re.match("[0-9]+/[0-9]+/[0-9]+", col ) ]
    # %%
    c_virus1 = c_virus[ date_cols ].sum().reset_index()
    c_virus1.columns = ['date_str', 'n_cases']
    c_virus1['log_n_cases'] = np.log( c_virus1['n_cases'] )
    # %%
    c_virus1['date'] = pd.to_datetime( c_virus1['date_str'], format='%m/%d/%y' )
    c_virus1.plot(x='date', y='log_n_cases')
    # %%
