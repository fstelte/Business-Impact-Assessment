# app/config.py
# Configuratie-instellingen voor de applicatie.

import os

# Bepaal de basisdirectory van het project
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Standaard configuratieklasse."""
    # Gebruik een sterke, geheime sleutel in productie!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'een-zeer-geheime-sleutel'
    
    # Configureer de SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'bia_tool.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
