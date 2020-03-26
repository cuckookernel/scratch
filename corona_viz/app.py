"""Implements routes for visualization app"""
from flask import Flask, Blueprint, Response, request

import datetime as dt
from jinja2 import Template
import corona_viz.common as common
from corona_viz.plots import get_plot, TRANSL_INV
from bokeh.resources import CDN
from redis import Redis

TMPL = Template("")  # html template loaded in create_app

route_bp = Blueprint('route_blueprint', __name__)
red = Redis("localhost")

# TODO: línea de Mundo entero
# TODO: mostrar fecha de última actualización de datos
# TODO: mostrar tasa de crecimiento
# TODO: Fit con término cuadrático

@route_bp.route('/corona_viz.html')
def main_linear():
    """main route page"""
    return render_html('linear')


@route_bp.route('/corona_viz_log.html')
def main_log():
    """main route page"""
    return render_html('log')


def render_html( scale: str ) -> str:
    """Render any of the versions"""
    # ip = request.ip.address
    ip = str(request.remote_addr)
    red.hincrby( f"/count_by_ip", ip )
    red.hincrby( f"/count_by_date", str(dt.date.today()) )
    red.hset( "/user-agent", ip, str(request.headers.get('User-Agent')) )
    red.hset( "/headers", ip, str(request.headers))

    reload_tmpl()  # TODO: take out
    x_tools = request.args.get("xt", "")
    x_countries = request.args.get("xc", "")

    if scale == "linear":
        other_view = f'<a href="/corona_viz_log.html?xt={x_tools}&xc={x_countries}">' \
                     f'Vista en escala logarítmica</a>'
    else:
        other_view = f'<a href="/corona_viz.html?xt={x_tools}&xc={x_countries}">' \
                     f'Vista en escala lineal</a>'

    return TMPL.render(resources=CDN.render(), scale=scale,
                       x_countries=x_countries, x_tools=x_tools,
                       other_view=other_view )


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

    plot_json = get_plot( klass=klass, scale=scale, x_tools=x_tools, x_countries=x_countries)
    return Response(plot_json, mimetype="application/json")


def create_app():
    """Return app for gunicorn to serve"""
    app = Flask(__name__)
    app.register_blueprint(route_bp)
    reload_tmpl()
    print(f"COVID_DATA_BASE={common.COVID_DATA_BASE}")
    print("create_app done.")
    return app


def reload_tmpl():
    with open("corona_viz/corona_viz.html") as f_in:
        global TMPL
        TMPL = Template(f_in.read())


def translate_ip_counts():
    # %%
    red = Redis("localhost")

    red.mget( '/ip')
    # %%
