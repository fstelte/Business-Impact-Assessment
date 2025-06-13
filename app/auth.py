# app/auth.py
# Behandelt de routes voor authenticatie (login, logout, register).

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from .forms import LoginForm, RegistrationForm
from .models import User
from . import db # bcrypt is hier niet meer nodig

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
    return render_template('auth/register.html', title='Registreren', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Route voor het inloggen van een gebruiker."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            # EXTRA CONTROLE: Is het account geactiveerd?
            if not user.is_active:
                flash('Your account has not been activated yest. You can login after an administrator has enabled your account.', 'warning')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Logged in successfully.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login faild, please check email and password.', 'danger')
    return render_template('auth/login.html', title='Login', form=form)





@auth.route('/logout')
def logout():
    """Route voor het uitloggen van de huidige gebruiker."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
