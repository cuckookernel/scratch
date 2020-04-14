"""Generate nice interactive visualization of coronavirus time series"""
# %%
from typing import List, Dict
import pandas as pd
import re
import numpy as np
import datetime as dt
import json

from bokeh.io import show
from bokeh.palettes import Category10
from bokeh.plotting import figure, Figure
from bokeh.models.formatters import DatetimeTickFormatter, NumeralTickFormatter
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.embed import json_item

import corona_viz.common as com
from corona_viz.common import TRANSL, DataCacheRec, PARQUET_PATH

DF = pd.DataFrame
Date = dt.date
# %%

COUNTRIES = [ "Colombia", "Mexico", "Brazil", "Venezuela",
              "Italy", "Spain", "US",  "Germany"]

ACTIVE_COUNTRIES = { "Colombia", "Mexico", "Spain" }

TRANSL_INV = { v: k for k, v in TRANSL.items() }


DATA_CACHE: Dict[dt.date, DataCacheRec] = {}  # date -> DF
# %%
# TODO: use multi_line for estimate


def get_cmp_plot( klass: str, scale: str = "linear", date: Date = None, **kwargs) -> str:

    data_rec = cntries_data( date )
    """Return plot as json"""
    plot = make_cmp_plot(data_rec.data, klass, scale, **kwargs)

    ret = json.dumps(json_item(plot, "klass"))

    return ret
    # %%


def cntries_data( date: Date = None ):
    return com.get_data(cache=DATA_CACHE,
                        date=date,
                        glob_str=str(PARQUET_PATH / "world/df_*.parquet"))


def make_cmp_plot(data: DF, klass: str, scale: str = "linear",
              x_tools: List[str] = None, countries: List[str] = None,
              x_countries: List[str] = None ):
    """Make a bokeh plot of a certain type (confirmed/recovered/deaths/active)
    scale can be "linear" or "log"
     for a bunch of countries"""

    x_countries = x_countries or []
    countries = countries or COUNTRIES
    print( 'c1', countries )
    if scale == 'log' and 'World' not in countries:
        countries = ['World'] + countries
    print('c2', countries)
    countries = x_countries + [ c for c in countries if c not in x_countries ]
    countries = countries[:10]

    p = init_plot( scale, x_tools )

    for country, color in zip(countries, Category10[10]):
        data_src = data_source_ctry( data, country )
        visible = country in (ACTIVE_COUNTRIES.union(x_countries))
        legend = TRANSL.get( country, country )
        draw_country_line(p, data_src, country, klass, color, visible, legend )

    set_hover_tool(p, klass)

    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.yaxis.formatter = NumeralTickFormatter(format='0,0')
    p.xaxis.formatter = DatetimeTickFormatter(days=["%b %d"])

    # output_file(OUTPUT_DIR / f"{klass}.html", title=f"Cases by country - {klass}")
    return p
    # %%


def init_plot(scale: str, x_tools: List[str]):
    """Initialize plot and set axis labels"""
    x_tools = [] if x_tools is None else x_tools
    tools = x_tools + "crosshair reset hover previewsave".split()  # pan,box_zoom

    y_axis_type = "log" if scale == "log" else "linear"

    p = figure(plot_width=696, plot_height=600, x_axis_type="datetime",
               y_axis_type=y_axis_type, tools=tools)
    # p.title.text = f'Corona virus by country - {klass.upper()} cases'
    p.xaxis.axis_label = "Fecha"
    p.yaxis.axis_label = ("Número de Casos"
                          + " (escala logarítmica)" if y_axis_type == "log" else "")

    return p


def data_source_ctry(  data: DF, country: str ) -> ColumnDataSource:
    """Draw line for one country and (possibly) the estimate"""

    df = data[data['country'] == country].copy()
    df['est_label'] = np.where( df['n_confirmed_est'].notnull(), " (estimado)", "")
    n = df[f'n_confirmed']
    df['n_or_est'] = n.where( n.notnull(), np.round(df['n_confirmed_est']) )

    df['date_str'] = df['date'].astype(str).str[:10]
    for col in ['n_active', 'n_deaths', 'n_recovered']:
        df[col + '_str'] = df[col].astype( str ).where( df[col].notnull(), '' )


    source = ColumnDataSource( data=df )

    return source


def draw_country_line( p: Figure, source: ColumnDataSource,
                       country: str, klass: str, color: str, visible: bool = True,
                       legend: str = None ):

    if legend is None:
        legend = TRANSL.get(country, country),

    p.line('date', f'n_{klass}',
           source=source,
           line_width=4, color=color, alpha=0.8,
           legend_label=legend,
           visible=visible)

    if klass == 'confirmed':
        p.line( 'date', 'n_confirmed_est',
                source=source,
                line_dash='dashed',
                line_width=2, color=color, alpha=0.8,
                legend_label=legend,
                visible=visible )


def set_hover_tool(p: Figure, klass: str):
    """Display a little sign when moving mouse over a point in the series"""
    hover = p.select(dict(type=HoverTool))

    total_data = f"@n_{klass}"
    if klass == 'confirmed':
        total_data = "@n_or_est @est_label"

    hover.tooltips = dict([
        # ("index", "$index"),
        # ("(xx,yy)", "(@x, @y)"),
        ( "País", "@pais"),
        ("Fecha", "@date_str"),
        (f"Total {TRANSL[klass]}", total_data),
    ])


def get_plot_cntry( country: str, scale: str = "linear", date: Date = None, **kwargs) -> str:
    """Return plot as json"""
    data_rec = com.get_data( cache=DATA_CACHE,
                             date=date,
                             glob_str=str(PARQUET_PATH / "world/df_*.parquet") )
    plot = make_plot_cntry(data_rec.data, country=country, scale=scale, **kwargs )

    ret = json.dumps(json_item(plot, "klass"))

    return ret
    # %%


def set_hover_tool_ctry(p: Figure):
    """Display a little sign when moving mouse over a point in the series"""
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = dict([
        # ("index", "$index"),
        # ("(xx,yy)", "(@x, @y)"),
        ("País", "@pais"),
        ("Fecha", "@date_str"),
        (f"Total activos", "@n_active_str"),
        (f"Total confirmados", "@n_or_est @est_label"),
        (f"Total recuperados", "@n_recovered_str"),
        (f"Total muertes", "@n_deaths_str"),
    ])


def make_plot_cntry(data: DF, scale: str = "linear", country="Colombia",
                    x_tools: List[str] = None):
    """Make a bokeh plot of a certain type (confirmed/recovered/deaths/active)
    scale can be "linear" or "log"
     for a bunch of countries"""

    klasses = ["active",  "deaths", "recovered", "confirmed"]

    p = init_plot( scale, x_tools=x_tools )

    data_source = data_source_ctry(data, country=country)

    all_colors = Category10[10]
    klass_2_color = {
        'active': all_colors[1],
        'recovered': all_colors[2],
        'deaths': all_colors[3],
        'confirmed': all_colors[0],
    }

    for klass in klasses:
        color = klass_2_color[klass]
        # visible = country in (ACTIVE_COUNTRIES.union(x_countries))
        draw_country_line(p, source=data_source, country=country, klass=klass,
                          legend=TRANSL.get(klass, klass), color=color, visible=True )
        # set_hover_tool(p, klass)
        set_hover_tool_ctry( p )

    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.yaxis.formatter = NumeralTickFormatter(format='0,0')
    p.xaxis.formatter = DatetimeTickFormatter(days=["%b %d"])

    # output_file(OUTPUT_DIR / f"{klass}.html", title=f"Cases by country - {klass}")
    return p
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


def interactive_testing():
    """Interactive testing"""
    # %%
    # noinspection PyUnresolvedReferences
    runfile( 'corona_viz/plots.py')
    data_rec = com.get_data( cache=DATA_CACHE, glob_str="df_*.parquet", date_col="date")
    data = data_rec.data
    # typ = "confirmed"
    plot = make_plot(data, klass="confirmed", scale="log")
    show(plot)
    # %%
    plot = make_plot(data, klass="confirmed", scale="linear")
    show(plot)
