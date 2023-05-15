# service_app_db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

class AppDb:

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        sqlalchemy_db_uri = app.config.get('SQLALCHEMY_DB_URI')
        sqlalchemy_engine_options = app.config.get('SQLALCHEMY_ENGINE_OPTIONS')

        engine = create_engine(
            sqlalchemy_db_uri,
            **sqlalchemy_engine_options
        )
        sqlalchemy_scoped_session = scoped_session(
            sessionmaker(
                bind=engine,
                expire_on_commit=False
            )
        )

        setattr(self, 'session', sqlalchemy_scoped_session)