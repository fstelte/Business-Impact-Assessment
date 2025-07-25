# app/auth.py
# Behandelt de routes voor authenticatie (login, logout, register).

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from .forms import LoginForm, RegistrationForm, MFAForm  # Voeg MFAForm toe hier
from .models import User
from . import db # bcrypt is hier niet meer nodig
from datetime import datetime, timedelta
import pyotp
import urllib.parse
import secrets
from .session_security import generate_session_fingerprint

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
                flash('Your account is not active. Please contact an administrator.', 'danger')
                return redirect(url_for('auth.login'))
            
            # Check if MFA is enabled
            if user.mfa_enabled:
                # Store user ID in session for MFA verification
                session['mfa_user_id'] = user.id
                session['mfa_timestamp'] = datetime.now().isoformat()
                return redirect(url_for('auth.verify_mfa'))
            else:
                # Complete login process
                login_user(user, remember=form.remember_me.data)
                flash('Please set up MFA to secure your account.', 'warning')
                return redirect(url_for('auth.setup_mfa'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/verify_mfa', methods=['GET', 'POST'])
def verify_mfa():
    if 'mfa_user_id' not in session:
        flash('Invalid MFA session. Please log in again.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Check MFA session timeout (5 minutes)
    if 'mfa_timestamp' in session:
        mfa_time = datetime.fromisoformat(session['mfa_timestamp'])
        if datetime.now() - mfa_time > timedelta(minutes=5):
            session.pop('mfa_user_id', None)
            session.pop('mfa_timestamp', None)
            flash('MFA session expired. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))
    
    form = MFAForm()
    if form.validate_on_submit():
        user = User.query.get(session['mfa_user_id'])
        if user and user.mfa_enabled:
            totp = pyotp.TOTP(user.mfa_secret)
            if totp.verify(form.token.data, valid_window=1):
                # Clear MFA session data
                session.pop('mfa_user_id', None)
                session.pop('mfa_timestamp', None)
                
                # Complete login process
                complete_login(user, False)  # Don't remember MFA logins
                return redirect(url_for('main.index'))
            else:
                flash('Invalid MFA token. Please try again.', 'danger')
        else:
            flash('MFA verification failed. Please log in again.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/verify_mfa.html', form=form)

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

def complete_login(user, remember_me=False):
    """Complete the login process with security measures."""
    login_user(user, remember=remember_me)
    
    # Set session security data
    session.permanent = True
    session['login_time'] = datetime.now().isoformat()
    session['last_activity'] = datetime.now().isoformat()
    session['session_fingerprint'] = generate_session_fingerprint()
    session['csrf_token'] = secrets.token_hex(16)
    
    flash(f'Welcome back, {user.username}!', 'success')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Clear all session data
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))