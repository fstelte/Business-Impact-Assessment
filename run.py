# run.py
# Dit is het startpunt van de applicatie.

from app import create_app, db
from app.models import User, ContextScope
from dotenv import load_dotenv

# Maak de Flask app instance aan met de 'default' configuratie
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Maakt een shell context aan die automatisch de database instance en modellen importeert
    wanneer 'flask shell' wordt uitgevoerd.
    """
    return {'db': db, 'User': User, 'BusinessProcess': ContextScope}

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0' , port='5001')
