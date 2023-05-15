# factory.py

from flask import Flask, request, g, url_for, current_app, render_template
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap4

from .services import app_logging, app_db
#from .model import from app.model import Context_Scope, Components, Availability_Requirements, References

def create_app():

    app = Flask(__name__)

    app.config.from_object('config.ConfigDevelopment')

    # services
    app.logger = app_logging.init_app(app)
    app_db.init_app(app)
    app.logger.debug('test debug message')

    Bootstrap4(app)

    csrf = CSRFProtect()
    csrf.init_app(app)

    # blueprints
    from .blueprints.manage_data.views import manage_data_blueprint
    app.register_blueprint(manage_data_blueprint, url_prefix='/manage-data')

    @app.teardown_appcontext
    def teardown_db(response_or_exception):
        if hasattr(app_db, 'session'):
            app_db.session.remove()

    @app.route('/')
    def index():
        #hours = app_db.session.query(Hours).order_by(Hours.id).all()
        return render_template(
            'home.html',
            welcome_message='Hello world',
            #hours=hours,
        )

    return app