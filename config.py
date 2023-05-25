# config.py

import os
from mysecrets import SECRET_KEY

project_dir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False    

class ConfigDevelopment(Config):
    DEBUG = True
    SECRET_KEY = SECRET_KEY
    SQLALCHEMY_DB_URI = 'sqlite:///' + os.path.join(project_dir, 'bia.db')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'echo': True,
    }

class ConfigTesting(Config):
    TESTING = True

class ConfigProduction(Config):
    pass