# app/auth.py
# Behandelt de routes voor authenticatie (login, logout, register).

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from .forms import LoginForm, RegistrationForm
from .models import User
from . import db # bcrypt is hier niet meer nodig

import pyotp
import urllib.parse


auth = Blueprint('auth', __name__)
@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Route voor het registreren van een nieuwe gebruiker."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        # De gebruiker wordt standaard als 'is_active=False' aangemaakt.
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can login after an administrator has enabled your account.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has not been activated yet. You can login after an administrator has enabled your account.', 'warning')
                return redirect(url_for('auth.login'))
            
            if user.mfa_enabled:
                session['user_id'] = user.id
                return redirect(url_for('auth.verify_mfa'))
            else:
                login_user(user, remember=form.remember_me.data)
                return redirect(url_for('auth.setup_mfa'))
        else:
            flash('Login failed, please check email and password.', 'danger')
    return render_template('auth/login.html', title='Login', form=form)
@auth.route('/verify_mfa', methods=['GET', 'POST'])
def verify_mfa():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(request.form['token']):
            login_user(user)
            session.pop('user_id', None)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid MFA token', 'danger')
    
    return render_template('auth/verify_mfa.html')

@auth.route('/setup_mfa', methods=['GET', 'POST'])
@login_required
def setup_mfa():
    # Genereer een geheime sleutel voor de gebruiker als deze nog niet bestaat
    if not current_user.mfa_secret:
        current_user.mfa_secret = pyotp.random_base32()
        db.session.commit()

    # Genereer de provisioning URL
    totp = pyotp.TOTP(current_user.mfa_secret)
    provisioning_url = totp.provisioning_uri(name=current_user.email, issuer_name="BIA Tool")

    # URL-encode de provisioning URL
    encoded_url = urllib.parse.quote(provisioning_url)

    if request.method == 'POST':
        # Verwerk de POST-aanvraag hier
        token = request.form.get('token')
        if totp.verify(token):
            current_user.mfa_enabled = True
            db.session.commit()
            flash('MFA has been successfully set up!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid token. Please try again.', 'danger')

    return render_template('auth/setup_mfa.html', provisioning_url=encoded_url, secret_key=current_user.mfa_secret)


@auth.route('/logout')
def logout():
    """Route voor het uitloggen van de huidige gebruiker."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
