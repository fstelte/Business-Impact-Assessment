# app/admin.py
# Routes specifiek voor de administrator.

from flask import Blueprint, render_template, abort, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from .models import User
from .forms import EditUserForm
from . import db
from flask_wtf.csrf import CSRFProtect

admin = Blueprint('admin', __name__)

# Custom decorator om te controleren of een gebruiker een admin is
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/users')
@login_required
@admin_required
def list_users():
    """Toont een lijst van alle gebruikers."""
    users = User.query.all()
    return render_template('admin/users.html', users=users, title="Gebruikersbeheer")

@admin.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Pagina om de rol van een gebruiker te bewerken."""
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        db.session.commit()
        flash(f'Gebruiker {user.username} is bijgewerkt.', 'success')
        return redirect(url_for('admin.list_users'))
        
    return render_template('admin/edit_user.html', form=form, user=user, title="Bewerk Gebruiker")

@admin.route('/user/<int:user_id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_user(user_id):
    """Route om een gebruiker te activeren."""
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash(f'Gebruiker {user.username} is geactiveerd.', 'success')
    return redirect(url_for('admin.list_users'))

@admin.route('/user/<int:user_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot deactivate yourself.', 'danger')
    else:
        user.is_active = False
        db.session.commit()
        flash(f'User {user.username} has been deactivated.', 'success')
    return redirect(url_for('admin.list_users'))