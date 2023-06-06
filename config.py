# config.py
import os

class Config(object):
    DEBUG = False
    TESTING = False    

class ConfigDevelopment(Config):

    SECRET_KEY = os.getenv('SECRET_KEY')
    if(SECRET_KEY is None):
        raise ValueError("No SECRET_KEY set please follow the README")
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    DEBUG = True
    SQLALCHEMY_DB_URI = 'sqlite:///' + os.path.join(project_dir, 'bia.db')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'echo': True,
    }

class ConfigTesting(Config):
    TESTING = True

class ConfigProduction(Config):
    pass