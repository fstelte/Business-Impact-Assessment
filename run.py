# Import environment variables from .env
from dotenv import load_dotenv
# Import factory function
from app import factory

app = factory.create_app()

if __name__ == '__main__':
    app.run(host= '0.0.0.0' , port='5000')