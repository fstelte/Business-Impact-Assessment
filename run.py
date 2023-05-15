# run.py

from app import factory

app = factory.create_app()

if __name__ == '__main__':
    app.run(host= '0.0.0.0')