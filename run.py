# Import environment variables from .env
from dotenv import load_dotenv
# Import factory function
from app import factory

app = factory.create_app()
# Load environment variables from .env
load_dotenv()

if __name__ == '__main__':
    app.run(host= '0.0.0.0' , port='5001')