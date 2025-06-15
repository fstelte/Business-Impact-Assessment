# app/admin.py
# Routes specifiek voor de administrator.

from flask import Blueprint, render_template, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from .models import User, ContextScope
from .forms import EditUserForm, ContextScopeOwnershipForm
from . import db

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from .models import ContextScope, User
from .forms import ContextScopeOwnershipForm
from . import db



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

@admin.route('/manage_context_scope_ownership/<int:context_scope_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_context_scope_ownership(context_scope_id):
    context_scope = ContextScope.query.get_or_404(context_scope_id)
    form = ContextScopeOwnershipForm()
    
    # Populate the choices for the SelectMultipleField
    form.users.choices = [(user.id, user.username) for user in User.query.all()]
    
    if form.validate_on_submit():
        selected_users = User.query.filter(User.id.in_(form.users.data)).all()
        context_scope.users = selected_users
        db.session.commit()
        flash('Context Scope ownership updated successfully.', 'success')
        return redirect(url_for('admin.list_context_scopes'))
    
    # Pre-select the current owners
    form.users.data = [user.id for user in context_scope.users]
    
    return render_template('admin/manage_context_scope_ownership.html', form=form, context_scope=context_scope)

@admin.route('/list_context_scopes')
@login_required
@admin_required
def list_context_scopes():
    context_scopes = ContextScope.query.all()
    return render_template('admin/list_context_scopes.html', context_scopes=context_scopes)