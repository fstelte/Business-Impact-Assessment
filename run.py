# run.py
# Dit is het startpunt van de applicatie.
import os
from app import create_app, db
# Pas dit aan met je daadwerkelijke modelnamen
from app.models import User, ContextScope
from dotenv import load_dotenv

# Laad de .env file HELEMAAL aan het begin
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    
# --- DE WIJZIGING IS HIER ---
# Lees de configuratienaam uit de environment variabelen.
# Als FLASK_CONFIG niet is ingesteld, wordt 'default' gebruikt.
config_name = os.getenv('FLASK_CONFIG') #or 'default'

# Maak de Flask app instance aan met de gekozen configuratie.
print(f"INFO: Applicatie wordt gestart met configuratie: '{config_name}'")
app = create_app(config_name)
# --- EINDE WIJZIGING ---

@app.shell_context_processor
def make_shell_context():
    """
    Maakt een shell context aan die automatisch de database instance en modellen importeert
    wanneer 'flask shell' wordt uitgevoerd.
    """
    # Zorg dat de naam hier overeenkomt met je model (ContextScope vs BusinessProcess)
    return {'db': db, 'User': User, 'ContextScope': ContextScope} 

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0' , port='5001')