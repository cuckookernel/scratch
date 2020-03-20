"""Implements routes for visualization app"""
from flask import Flask, Blueprint, Response, request

from jinja2 import Template
from corona_viz.plots import get_plot
from bokeh.resources import CDN

TMPL = Template("")  # html template loaded in create_app

route_bp = Blueprint('route_blueprint', __name__)


@route_bp.route('/corona_viz.html')
def main_linear():
    """main route page"""
    reload_tmpl()  # TODO: take out
    return TMPL.render(resources=CDN.render(), scale="linear",
                       other_view='<a href="/corona_viz_log.html">logarítmica</a>' )


@route_bp.route('/corona_viz_log.html')
def main_log():
    """main route page"""
    reload_tmpl()  # TODO: take out
    return TMPL.render(resources=CDN.render(), scale="log",
                       other_view='<a href="/corona_viz.html">lineal</a>')


@route_bp.route('/cvv_plot.json')
def cvv_plot():
    """main route"""
    klass = request.args.get("k")
    scale = request.args.get("s")

    plot_json = get_plot( klass=klass, scale=scale )
    return Response(plot_json, mimetype="application/json")


def create_app():
    """Return app for gunicorn to serve"""
    app = Flask(__name__)
    app.register_blueprint(route_bp)
    reload_tmpl()
    print("create_app done.")
    return app


def reload_tmpl():
    with open("corona_viz/corona_viz.html") as f_in:
        global TMPL
        TMPL = Template(f_in.read())
