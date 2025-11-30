from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def require_roles(*allowed_roles, redirect_endpoint='index'):
    """
    Centralized role-based access decorator.
    
    Usage:
    @require_roles('admin')
    @require_roles('admin', 'teacher')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("You must be logged in to access this page.", "danger")
                return redirect(url_for('auth.login'))  # Assuming you have auth.login route
            
            # Make sure current_user has a role attribute
            user_role = getattr(current_user, 'role', None)
            if not user_role or user_role not in allowed_roles:
                flash("You do not have permission to access this page!", "danger")
                return redirect(url_for(redirect_endpoint))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
