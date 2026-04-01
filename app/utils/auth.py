from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def require_roles(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash("You don't have permission to access this page.", 'danger')
                return redirect(url_for('dashboard.dashboard_home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
