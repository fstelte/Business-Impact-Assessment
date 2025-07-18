from flask import session, request, redirect, url_for, flash, g
from flask_login import current_user, logout_user
from datetime import datetime, timedelta
from functools import wraps
import secrets

def init_session_security(app):
    """Initialize session security for the Flask app."""
    
    @app.before_request
    def check_session_security():
        """Check session validity before each request."""
        
        # Skip security checks for static files and auth routes
        if (request.endpoint and 
            (request.endpoint.startswith('static') or 
             request.endpoint in ['auth.login', 'auth.register', 'auth.logout'])):
            return
        
        # Check if user is authenticated
        if current_user.is_authenticated:
            # Check session timeout
            if 'last_activity' in session:
                last_activity = datetime.fromisoformat(session['last_activity'])
                if datetime.now() - last_activity > timedelta(hours=12):
                    logout_user()
                    session.clear()
                    flash('Your session has expired. Please log in again.', 'warning')
                    return redirect(url_for('auth.login'))
            
            # Check session fingerprint (prevent session hijacking)
            current_fingerprint = generate_session_fingerprint()
            if 'session_fingerprint' in session:
                if session['session_fingerprint'] != current_fingerprint:
                    logout_user()
                    session.clear()
                    flash('Security violation detected. Please log in again.', 'danger')
                    return redirect(url_for('auth.login'))
            else:
                session['session_fingerprint'] = current_fingerprint
            
            # Update last activity timestamp
            session['last_activity'] = datetime.now().isoformat()
            session.permanent = True

def generate_session_fingerprint():
    """Generate a fingerprint for the current session to prevent hijacking."""
    user_agent = request.headers.get('User-Agent', '')
    # Note: Don't use IP address as it can change legitimately
    return hash(user_agent)

def require_fresh_login(max_age_minutes=30):
    """Decorator to require fresh login for sensitive operations."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # Check if login is fresh enough
            if 'login_time' in session:
                login_time = datetime.fromisoformat(session['login_time'])
                if datetime.now() - login_time > timedelta(minutes=max_age_minutes):
                    flash('This action requires recent authentication. Please log in again.', 'warning')
                    return redirect(url_for('auth.login', next=request.url))
            else:
                # No login time recorded, require fresh login
                flash('This action requires recent authentication. Please log in again.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator