# services.py

from .service_app_logging import AppLogging
from .service_app_db import AppDb

app_logging = AppLogging()
app_db = AppDb()