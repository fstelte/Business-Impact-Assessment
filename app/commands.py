# app/commands.py
# Definieert custom CLI commando's voor de applicatie.

import click
from flask.cli import with_appcontext
from . import db
from .models import User
import os

@click.command('create-admin')
@with_appcontext
def create_admin_command():
    """Maakt een admin gebruiker aan via de command-line."""
    
    # Haal credentials op uit environment variables voor veiligheid
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if not admin_email or not admin_password:
        click.echo('Error: ADMIN_EMAIL en ADMIN_PASSWORD environment variables moeten zijn ingesteld.')
        return

    # Controleer of de gebruiker al bestaat
    if User.query.filter_by(email=admin_email).first():
        click.echo(f'User with email {admin_email} already exists.')
        return
    
    # Maak de admin gebruiker aan
    admin_user = User(
        username='admin',
        email=admin_email,
        role='admin', # Belangrijk: zet de rol op 'admin'
        active=True
    )
    admin_user.set_password(admin_password)
    
    db.session.add(admin_user)
    db.session.commit()
    
    click.echo(f'Admin user {admin_email} successfully created.')

def init_app(app):
    """Registreert de CLI commando's bij de app."""
    app.cli.add_command(create_admin_command)

