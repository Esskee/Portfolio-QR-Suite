import dash  # (version 1.12.0) pip install dash
import dash_bootstrap_components as dbc

from layout import applayout
from callbacks import register_callbacks

meta_viewport = {'name': 'viewport',
                 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}
stylesheet = [dbc.themes.LUX]

dashapp = dash.Dash(__name__,
                    title="My Title",
                    external_stylesheets=stylesheet,
                    suppress_callback_exceptions=True,
                    url_base_pathname='/',
                    meta_tags=[meta_viewport])

dashapp.layout = applayout

register_callbacks(dashapp)
