# app/__init__.py
# Dit bestand bevat de application factory.

from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
# --- GEWIJZIGD: Importeer het 'config' dictionary uit je config.py ---
from .config import config  # Let op: 'config' in kleine letters
from flask_wtf.csrf import CSRFProtect
from .config import DefaultConfig

# Deze initialisaties blijven hetzelfde
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to view this page.'
login_manager.login_message_category = 'info'

# --- GEWIJZIGD: De functie accepteert nu een 'config_name' string ---
def create_app(config_name='default'):
    """De application factory functie."""
    app = Flask(__name__, instance_relative_config=True)

    # --- VERWIJDERD: De hardcoded SECRET_KEY is weg! ---
    # app.config['SECRET_KEY'] = 'your-secret-key' # DIT IS NIET VEILIG

    # --- GEWIJZIGD: Laad de configuratie op basis van de naam ---
    # Deze regel laadt ALLE configuratie-instellingen (incl. SECRET_KEY en DATABASE_URI)
    # uit de juiste klasse (bv. ProductionConfig of DevelopmentConfig).
    app.config.from_object(DefaultConfig)

    # De initialisaties van de extensies blijven hetzelfde.
    # Ze gebruiken nu de configuratie die hierboven is geladen.
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # De rest van je bestand blijft ongewijzigd, dit is al perfect!
    # -----------------------------------------------------------------

    # Registreer de blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Registreer de admin blueprint
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
                return value
        return value.strftime(format)

    return app