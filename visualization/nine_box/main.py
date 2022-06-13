
# import sqlite3 as sql
from os.path import dirname, join

import pandas as pd
import numpy as np
import os

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select  # , Slider, TextInput
from bokeh.plotting import figure, Figure
from bokeh.resources import CDN
from bokeh.embed import file_html

DATA_PATH1 = 'nine_box/Resultados_de_performance.xlsx'
DATA_PATH2 = 'nine_box/Resultados_de_performance_tech_leads.xlsx'

level = os.getenv('LEVEL', 'Mid')
LEVELS = [ level ]

DF = pd.DataFrame

# Create Input controls
# reviews = Slider(title="Minimum number of reviews", value=80, start=10, end=300, step=10)
# min_year = Slider(title="Year released", start=1940, end=2014, value=1970, step=1)
# max_year = Slider(title="End Year released", start=1940, end=2014, value=2014, step=1)
# oscars = Slider(title="Minimum number of Oscar wins", start=0, end=4, value=0, step=1)
# boxoffice = Slider(title="Dollars at Box Office (millions)", start=0, end=800, value=0, step=1)
# director = TextInput(title="Director name contains")
# cast = TextInput(title="Cast names contains")
# x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Tomato Meter")
# y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Number of Reviews")

# Create Column Data Source that will be used by the plot


TOOLTIPS = [
    ("Name", "@name"),
    ("Level", "@level"),
    ("Overall Score Pctile", "@calif_pctile0"),
    ("TP&E Pctile", "@tpne_pctile0"),
    ("P&L Pctile", "@pnl_pctile0"),
]

FIG_WIDTH = 100
MARKER_SIZE = 7


def _main():
    devs_df = _get_data()

    source = ColumnDataSource( data=dict( x=[], y=[],
                                          color=[], name=[],
                                          overall_pctile=[],
                                          revenue=[], alpha=[] ) )

    desc_txt = f"<h2>Visualization of LH Developers evaluation - {LEVELS[0]}</h2>" \
               f"<p>Hover on dots to see details of each developer</p>"

    desc = Div( text=desc_txt )  # , sizing_mode="stretch_width" )

    fig = _build_scatter_2d(source)
    one_dim = _build_one_dim(source)

    level = LEVELS[0]
    # level = Select( title="Level", value=LEVELS[0], options=LEVELS, height=15 )
    # controls = [level]
    # for control in controls:
    #    control.on_change('value', lambda attr, old, new: _update0() )

    widget_col = column( row( desc, height=80, width=600),
                         # row( column(*controls), height=55, width=500),
                         one_dim, fig,
                         sizing_mode='fixed', width=600, height=1200 )  # sizing_mode="scale_both")
    # model = column(desc, row(inputs, fig), sizing_mode="scale_both")

    def _update0():
        _update(source, one_dim, fig, devs_df, level )

    _update0()  # initial load of the data

    curdoc().add_root(widget_col)
    curdoc().title = "LH Dev Evaluations"

    _make_html(curdoc())


def _build_scatter_2d(source):
    fig = figure( plot_height=70,
                  plot_width=FIG_WIDTH,
                  # width=FIG_WIDTH,
                  title="Nine Box",
                  toolbar_location=None,
                  tooltips=TOOLTIPS,
                  sizing_mode="scale_both" )

    fig.circle( source=source, x="pnl_pctile", y="tpne_pctile",
                size=7, color="color", line_color=None, fill_alpha="alpha" )

    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None

    fig.line( x=[33, 33], y=[0, 100], line_width=1, line_color="#777777", line_dash="dashed" )
    fig.line( x=[67, 67], y=[0, 100], line_width=1, line_color="#777777", line_dash="dashed" )
    fig.line( y=[67, 67], x=[0, 100], line_width=1, line_color="#777777", line_dash="dashed" )
    fig.line( y=[33, 33], x=[0, 100], line_width=1, line_color="#777777", line_dash="dashed" )

    return fig


def _build_one_dim( source ):
    one_dim = figure( plot_height=20,
                      plot_width=FIG_WIDTH,
                      # width=FIG_WIDTH,
                      title="Overall Calif",
                      toolbar_location=None,
                      tooltips=TOOLTIPS,
                      sizing_mode="scale_both" )

    one_dim.xaxis.axis_label = "Overall Score (pctile)"
    one_dim.yaxis.visible = False
    one_dim.circle( source=source, x='calif_pctile0', y='rnd_y', color='color', size=MARKER_SIZE )

    return one_dim


def _get_data() -> DF:
    extract_cols = ['Persona', 'Calificación Pctil', 'P&L Pctile', 'TP&E Pctile']

    mids_df = pd.read_excel(DATA_PATH1, sheet_name='Mids', skiprows=1 )
    mids_df = mids_df[ extract_cols ]
    mids_df['level'] = 'Mid'

    seniors_df = pd.read_excel(DATA_PATH1, sheet_name='Senior', skiprows=1 )
    seniors_df = seniors_df[ extract_cols ]
    seniors_df['level'] = 'Senior'

    tleads_df = pd.read_excel(DATA_PATH2, sheet_name='Tech Leads', skiprows=1 )
    tleads_df = tleads_df[ extract_cols ]
    tleads_df['level'] = 'Tech Lead'

    print( tleads_df )
    print( tleads_df.isnull().sum() )

    devs_df = pd.concat( [mids_df, seniors_df, tleads_df] )
    devs_df = devs_df.rename( columns={'Persona': 'name',
                                       'P&L Pctile': 'pnl_pctile0',
                                       'TP&E Pctile': 'tpne_pctile0',
                                       'Calificación Pctil': 'calif_pctile0'})

    devs_df = devs_df[ devs_df.name.notnull() & devs_df['tpne_pctile0'].notnull() ]
    n_devs = len(devs_df)

    # print( f"n_devs: {n_devs}\n{devs_df[ devs_df.calif_pctile0.isnull() ]}" )
    # add some jitter to avoid overlapping dots
    devs_df['pnl_pctile'] = devs_df['pnl_pctile0'] + np.random.uniform( 0, 2, (n_devs,) )
    devs_df['tpne_pctile'] = devs_df['tpne_pctile0'] + np.random.uniform( 0, 2, (n_devs,) )
    devs_df['rnd_y'] = np.random.uniform( 0, 10, (n_devs,) )

    print( "count of null:", devs_df['calif_pctile0'].isnull().sum() )

    devs_df['color'] = devs_df['calif_pctile0'].map( lambda calif: get_rgb_color(calif, 0, 100) )
    devs_df['alpha'] = 0.8

    return devs_df


def _update( source: ColumnDataSource, one_dim: Figure, fig: Figure, devs_df: DF, level ):
    df = _select_devs( devs_df, level )

    one_dim.title.text = "%d devs selected" % len( df )

    fig.xaxis.axis_label = "People & Leadership Pctile"
    fig.yaxis.axis_label = "Technical Performance & Excellence Pctile"

    source.data = dict(
        calif_pctile0=df['calif_pctile0'],
        rnd_y=df['rnd_y'],
        pnl_pctile=df["pnl_pctile"],
        tpne_pctile=df["tpne_pctile"],
        pnl_pctile0=df["pnl_pctile0"],
        tpne_pctile0=df["tpne_pctile0"],
        level=df['level'],
        color=df["color"],
        name=df["name"],
        alpha=df['alpha']
    )


def get_rgb_color(val: float, low: float, high: float):

    color_high = (62, 207, 175)
    color_low = (57, 72, 255)

    lamb = (val - low) / (high - low)

    def _combine( hi, lo ):
        return int( hi * lamb + lo * (1-lamb) )

    rgb = map( _combine, color_high, color_low )

    rgb_color = '#%02x%02x%02x' % tuple(rgb)

    return rgb_color


def _select_devs( devs_df: DF, level ):

    level_val = level if isinstance( level, str ) else level.value
    selected = devs_df

    if level_val == 'Mid + Senior':
        print( f"level_val = '{level_val}'" )
        selected = selected[selected.level.isin( ['Mid', 'Senior'] )]
        print( f'selected has {len( selected )}' )

    elif level_val != "All - including Tech Leads":
        print(f"level_val = '{level_val}'")
        selected = selected[selected.level.str.contains(level_val)]
        print(f'selected has {len(selected)}')

    return selected


def _make_html( doc: Figure ):
    html = file_html( doc, CDN, "my plot" )

    f"nine_box_{LEVELS[0]}.html"

    with open( f"nine_box_{LEVELS[0]}.html", "w" ) as f_out:
        f_out.write(html)


_main()

# %%
