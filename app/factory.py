# factory.py

from flask import Flask, request, g, url_for, current_app, render_template
from markupsafe import Markup
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap5

from .services import app_logging, app_db
#from .model import from app.model import Context_Scope, Components, Availability_Requirements, References

def create_app():

    app = Flask(__name__)

    app.config.from_object('config.ConfigDevelopment')

    # services
    app.logger = app_logging.init_app(app)
    app_db.init_app(app)
    app.logger.debug('test debug message')

    Bootstrap5(app)

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
        welcome_message = Markup("""
    <h1>Business Impact Assessment</h1>
    <p>This app allows you to conduct Business Impact Assessments. Start under the **BIA** section.</p>
    <p>**Components** must be linked to a BIA.</p>
    <p>Components are then assigned **consequences**.</p>
    <p>**Availability requirements** will be specified for each component.</p>
    <p>Use the last tab to determine the **impact** per component.</p>
    <h1>Business Impact Assessment</h1>
    <p>Via de ze app kunnen Business Impact Assessment uitgevoerd worden. Begin bij het kopje BIA.</p>
    <p>Aan een BIA moeten componenten gekoppeld worden.</p>
    <p>Componenten krijgen weer consequenties toegewezen.</p>
    <p>Per component zullen de beschikbaarheidsvereisten op gegeven worden</p>
    <p>Gebruik het laatste tabblad om de impact te bepalen per component.</p>
    """)
        return render_template('home.html',welcome_message=welcome_message)
   


    return app
