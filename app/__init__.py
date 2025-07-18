# Dit bestand bevat de application factory.

from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_moment import Moment
from version import VERSION
from .session_security import init_session_security
from .security_headers import init_security_headers

# Deze initialisaties blijven hetzelfde
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()
moment = Moment()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

def create_app(config_class=None):
    """De application factory functie."""
    app = Flask(__name__)

    # Als geen config_class is gegeven, gebruik de DefaultConfig
    if config_class is None:
        from .config import DefaultConfig
        config_class = DefaultConfig

    # Laad de configuratie
    app.config.from_object(config_class)

    # Debug: print de database URI om te controleren
    print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    # Initialiseer de extensies
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)

    # Initialize session security
    init_session_security(app)

    # Initialize security headers
    init_security_headers(app)

    # Make session info available in templates
    @app.context_processor
    def inject_session_info():
        from .utils import get_session_info
        return dict(get_session_info=get_session_info)

    # Registreer de blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Registreer de admin blueprint
    from app.admin import admin
    app.register_blueprint(admin, url_prefix='/admin')

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

    @app.template_filter('impact_color')
    def impact_color_filter(impact_level):
        """Template filter voor impact kleuren"""
        if not impact_level:
            return 'bg-secondary'
        
        impact_lower = str(impact_level).lower().strip()
        
        # Very Low / Insignificant
        if impact_lower in ['very low', 'insignificant', '1']:
            return 'bg-green'
        
        # Low / Minor  
        elif impact_lower in ['low', 'minor', '2']:
            return 'bg-yellow'
        
        # Medium / Moderate
        elif impact_lower in ['medium', 'moderate', '3']:
            return 'bg-orange'
        
        # High / Major
        elif impact_lower in ['high', 'major', '4']:
            return 'bg-red'
        
        # Very High / Catastrophic
        elif impact_lower in ['very high', 'catastrophic', '5']:
            return 'bg-dark-red'
        
        # Default voor onbekende waarden
        else:
            return 'bg-secondary'

    @app.context_processor
    def inject_version():
        return dict(app_version=VERSION)

    return app