# app/config.py
# Configuratie-instellingen voor de applicatie.

import os
from dotenv import load_dotenv
from datetime import timedelta

# Laad de environment variabelen uit het .env bestand
load_dotenv()

# Bepaal de basisdirectory van het project
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Basisconfiguratie"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'een-zeer-geheim-wachtwoord'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session Security Configuration (OWASP recommendations)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)  # 12-hour session timeout
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS attacks
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    REMEMBER_COOKIE_SECURE = True  # Secure remember me cookies
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(hours=12)  # Also limit remember me duration
    
    # Additional security headers
    WTF_CSRF_TIME_LIMIT = None  # Let session timeout handle this

class SQLiteConfig(Config):
    # Configureer de SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'bia_tool.db')

class MariaDBConfig(Config):
    """Productieconfiguratie (gebruikt MariaDB uit .env)"""
    # Haal de database-onderdelen uit de environment
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')

    # Controleer of alle variabelen aanwezig zijn
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        raise ValueError("Database credentials are not completely filled out in the .env file")

    # Bouw de uiteindelijke connectie-string
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Lees het databasetype uit de omgevingsvariabelen
DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite').lower()

# Een dictionary om makkelijk de juiste config te kiezen
config = {
    'sqlite': SQLiteConfig,
    'mariadb': MariaDBConfig,
}

# Kies de juiste configuratie op basis van DATABASE_TYPE
if DATABASE_TYPE not in config:
    print(f"Warning: Unknown DATABASE_TYPE '{DATABASE_TYPE}'. Defaulting to SQLite.")
    DefaultConfig = SQLiteConfig
else:
    DefaultConfig = config[DATABASE_TYPE]

print(f"Using database configuration: {DefaultConfig.__name__}")
