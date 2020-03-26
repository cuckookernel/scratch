"""Implements routes for visualization app"""
import datetime as dt
from flask import Flask, Blueprint, Response, request
from redis import Redis

from bokeh.resources import CDN
from jinja2 import Template
import corona_viz.common as common
import corona_viz.colombia as col
from corona_viz.plots import get_plot, TRANSL_INV

# html templates loaded in create_app
TMPLS = { "world": Template(""),
          "col": Template("") }

route_bp = Blueprint('route_blueprint', __name__)
red = Redis("localhost")

# TODO: línea de Mundo entero
# TODO: mostrar fecha de última actualización de datos
# TODO: mostrar tasa de crecimiento
# TODO: Fit con término cuadrático


@route_bp.route('/corona_viz.html')
def corona_viz():
    """main route page"""
    # return render_html_world('linear')
    return render_html_col()


@route_bp.route('/corona_viz_log.html')
def corona_viz_log():
    """main route page"""
    return render_html_world('log')


@route_bp.route('/corona_viz_col.html')
def corona_viz_col():
    """main route page"""
    return render_html_col()


def render_html_world( scale: str ) -> str:
    """Render any of the versions"""
    # ip = request.ip.address
    print( f'render_html_world - scale: {scale}' )
    record_visit()
    reload_tmpls()  # TODO: take out
    x_tools = request.args.get("xt", "")
    x_countries = request.args.get("xc", "")

    if scale == "linear":
        other_view = f'<a href="/corona_viz_log.html?xt={x_tools}&xc={x_countries}">' \
                     f'Vista en escala logarítmica</a>'
    else:
        other_view = f'<a href="/corona_viz.html?xt={x_tools}&xc={x_countries}">' \
                     f'Vista en escala lineal</a>'

    return TMPLS['world'].render(resources=CDN.render(), scale=scale,
                                 x_countries=x_countries, x_tools=x_tools,
                                 other_view=other_view )


def render_html_col( ) -> str:
    """Render any of the versions"""
    # ip = request.ip.address
    record_visit()
    reload_tmpls()  # TODO: take out
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

    plot_json = get_plot( klass=klass, scale=scale, x_tools=x_tools,
                          countries=countries, x_countries=x_countries)
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
    print(f"COVID_DATA_BASE={common.COVID_DATA_BASE}")
    print("create_app done.")
    return app


def reload_tmpls():
    """Reload tmpl from html file"""
    global TMPLS

    with open("corona_viz/corona_viz.html") as f_in:
        TMPLS['world'] = Template(f_in.read())

    with open("corona_viz/corona_viz_col.html") as f_in:
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
