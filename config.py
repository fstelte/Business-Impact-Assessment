# config.py

import os

project_dir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False    

class ConfigDevelopment(Config):
    DEBUG = True
    SECRET_KEY = 'NO8py79NIOU7694rgLKJHIGo87tKUGT97g'
    SQLALCHEMY_DB_URI = 'sqlite:///' + os.path.join(project_dir, 'bia.db')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'echo': True,
    }

class ConfigTesting(Config):
    TESTING = True

class ConfigProduction(Config):
    pass