# Dash app initialization
import dash
# User management initialization
import os
from db_mgt import db
from config import config
import dash_bootstrap_components as dbc

from datetime import timedelta


FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"
# BOOTSTRAP_CSS = "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME]
# external_stylesheets=[FONT_AWESOME, BOOTSTRAP_CSS]
external_scripts = ["https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js", "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js"]


app = dash.Dash(
    __name__,
    meta_tags=[
        {
            'charset': 'utf-8',
        },
        {
            'name': 'viewport',
            'content': 'width=device-width, initial-scale=1, shrink-to-fit=no'
        }
    ],
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts
)
server = app.server
app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True



# config
server.config.update(
    # SECRET_KEY=os.urandom(12),
    SECRET_KEY="adsfadsfafradcvcvaerfqadsv324123dsaf",
    # SQLALCHEMY_DATABASE_URI=config.get('database', 'sqlcon'),
    # SQLALCHEMY_TRACK_MODIFICATIONS=False
)

server.config['SESSION_PERMANENT'] = True
server.config['SESSION_TYPE'] = 'filesystem'
server.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
server.config['SESSION_FILE_THRESHOLD'] = 500  

# db.init_app(server)