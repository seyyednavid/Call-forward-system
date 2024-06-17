"""
Initializes default settings for edgelit buttons in the database.
Checks for existing settings and populates with defaults if none are found.
"""


from .models import Settings, ButtonRange
from . import db

def add_settings():
    """
    Populates the database with default settings if empty.

    Creates 100 settings with predefined values for attributes like flash speed,
    number of flashes, and colors (on, off, free, busy) and commits them to the database.
    """
    if Settings.query.count() == 0:
        settings = [Settings(flashspeededgelit='4', numofflashes='5', on_color='#0000FF', off_color='#000000', free_color='#00FF00', busy_color='#FF0000') for _ in range(100)]
        db.session.bulk_save_objects(settings)
        db.session.commit()
        print("100 new settings added.")
    else:
        print("Settings already exist.")