# app/__init__.py
# Dit bestand bevat de application factory.

from flask import Flask
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from .config import Config
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to view this page.'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    """De application factory functie."""
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Zorg ervoor dat je een geheime sleutel hebt ingesteld
    csrf.init_app(app)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Registreer de blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Registreer de admin blueprint (zie volgende stap)
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    # Registreer de CLI commando's
    from . import commands
    commands.init_app(app)
    @app.template_filter('date')
    def date_filter(value, format='%Y'):
        if value == 'now':
            value = datetime.now()
        elif isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value  # Return the original string if it can't be parsed
        return value.strftime(format)

    return app
