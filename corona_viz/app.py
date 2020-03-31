"""Implements routes for visualization app"""
import datetime as dt
from flask import Flask, Blueprint, Response, request
from redis import Redis

from bokeh.resources import CDN
from jinja2 import Template
from corona_viz.common import tstamp_to_dt, COVID_DATA_BASE
import corona_viz.colombia as col
from corona_viz.plots import get_cmp_plot, get_plot_cntry, cntries_data, TRANSL_INV

# html templates loaded in create_app
TMPLS = { "world": Template(""),
          "col": Template("") }

route_bp = Blueprint('route_blueprint', __name__)
red = Redis("localhost")

# TODO: mostrar tasa de crecimiento
# TODO: Mapa colombia, deptos / municipios
# TODO: Por rango edad/sexo barritas
# TODO: Página mundo

@route_bp.route('/corona_viz.html')
def corona_viz():
    """main route page"""
    # return render_html_world('linear')
    return render_html_col()


@route_bp.route('/corona_viz_log.html')
def corona_viz_log():
    """main route page"""
    return render_html_cmp('log')


@route_bp.route('/corona_viz_lin.html')
def corona_viz_lin():
    """main route page"""
    return render_html_cmp('linear')


@route_bp.route('/corona_viz_col.html')
def corona_viz_col():
    """main route page"""
    return render_html_col()


@route_bp.route('/r/<string:fname>.<string:ext>')
def resource(fname: str, ext: str):
    """Fetch a static resource such as css or js"""
    by_ext = {'css': ( 'corona_viz/styles/{fname}.css',
                       'text/css'),
              'js':  ( 'corona_viz/js/{fname}.js',
                       'application/javascript')}

    tmpl, content_type = by_ext[ext]

    with open( tmpl.format(fname=fname) ) as f_in:
        ret = f_in.read()

    return Response(ret, content_type=content_type )


def render_html_cmp( scale: str ) -> str:
    """Render any of the versions"""
    # ip = request.ip.address
    print( f'render_html_world - scale: {scale}' )
    record_visit()
    reload_tmpls()
    last_mtime = tstamp_to_dt( cntries_data( date=None ).mtime ).isoformat(sep=' ')[:-10] + ' UTC'
    x_tools = request.args.get("xt", "")
    x_countries = request.args.get("xc", "")

    if scale == "linear":
        other_view = f'<a href="/corona_viz_log.html?xt={x_tools}&xc={x_countries}">' \
                     f'Vista en escala logarítmica</a>'
    else:
        other_view = f'<a href="/corona_viz_lin.html?xt={x_tools}&xc={x_countries}">' \
                     f'Vista en escala lineal</a>'

    return TMPLS['cmp'].render(resources=CDN.render(), scale=scale,
                               x_countries=x_countries, x_tools=x_tools,
                               other_view=other_view,
                               last_mtime=last_mtime)


def render_html_col( ) -> str:
    """Render any of the versions"""
    # ip = request.ip.address
    record_visit()
    reload_tmpls()
    x_tools = request.args.get("xt", "")
    htmls = col.get_htmls()

    return TMPLS['col'].render(resources=CDN.render(),
                               x_tools=x_tools,
                               **htmls)


@route_bp.route('/cvv_plot.json')
def cvv_plot():
    """main route"""
    klass = request.args.get("k")
    scale = request.args.get("s")
    x_tools = request.args.get("xt")
    x_tools = x_tools.split(",") if x_tools else None

    x_countries = request.args.get("xc")
    x_countries = x_countries.split(",") if x_countries else []
    x_countries = [ TRANSL_INV.get(ctr, ctr) for ctr in x_countries ]

    countries = request.args.get("c")
    countries = countries.split(",") if countries else []

    plot_json = get_cmp_plot( klass=klass, scale=scale, x_tools=x_tools,
                              countries=countries, x_countries=x_countries)
    return Response(plot_json, mimetype="application/json")


@route_bp.route('/cntry_plot.json')
def cntry_plot():
    """main route"""

    scale = request.args.get("s")
    x_tools = request.args.get("xt")
    x_tools = x_tools.split(",") if x_tools else None

    country = request.args.get("c")

    plot_json = get_plot_cntry( scale=scale, country=country, x_tools=x_tools)
    return Response(plot_json, mimetype="application/json")


def record_visit():
    """Record stats in redis"""
    ip = str(request.remote_addr)
    red.hincrby( f"/count_by_ip", ip )
    red.hincrby( f"/count_by_date", str(dt.date.today()) )
    red.hset( "/user-agent", ip, str(request.headers.get('User-Agent')) )
    red.hset( "/headers", ip, str(request.headers))


def create_app():
    """Return app for gunicorn to serve"""
    app = Flask(__name__)
    app.register_blueprint(route_bp)
    reload_tmpls()
    print(f"COVID_DATA_BASE={COVID_DATA_BASE}")
    print("create_app done.")
    return app


def reload_tmpls():
    """Reload tmpl from html file"""
    global TMPLS

    with open("corona_viz/html/corona_viz.html") as f_in:
        TMPLS['cmp'] = Template(f_in.read())

    with open("corona_viz/html/corona_viz_col.html") as f_in:
        TMPLS['col'] = Template(f_in.read())


def translate_ip_counts():
    """Copy counts from individual keys to /count_by_ip hash"""
    # %%
    # red = Redis("localhost")

    keys = red.keys( '/ip/*' )

    for k in keys:
        v = red.get(k)
        ip = k.split( '/')[2]
        red.hset( '/count_by_ip', ip, v )
    # %%
