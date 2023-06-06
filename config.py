# config.py
import os
from dotenv import load_dotenv

class Config(object):
    DEBUG = False
    TESTING = False    

class ConfigDevelopment(Config):

    # Load environment variables from .env
    load_dotenv()
    if 'SECRET_KEY' in os.environ:
       SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
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