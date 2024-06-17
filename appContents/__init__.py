"""
Initializes the Flask application, configures settings, sets up the database, and imports routes and models.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from pathlib import Path
import sys
import webbrowser
import pyautogui
import time

# Initialize Flask application
app = Flask(__name__, static_folder='static')
# Load configuration from the Config class
app.config.from_object(Config)

# Determine the root path of the application
def get_root_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent.parent

# Ensure the instance directory exists
db_dir = get_root_path() / 'instance'
db_dir.mkdir(parents=True, exist_ok=True)

# Database URI configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_dir}/site.db'

# Initialize SQLAlchemy with the app instance
db = SQLAlchemy(app)

# Import parts of your application that define routes and database models
from . import models, websocket, routes

def open_browser():
    """
    Opens the default web browser with the home page and enters fullscreen mode.
    """
    web_url = f"http://{Config.COMBINED_FLASK_IP_PORT}/callforward"
    webbrowser.open(web_url)
    time.sleep(4)
    pyautogui.press('f11')


