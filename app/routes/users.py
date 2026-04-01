from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import select
from app import db
from app.models import User
from app.utils.auth import require_roles

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@login_required
@require_roles('admin')
def list_users():
    users = db.session.execute(select(User).order_by(User.id.desc())).scalars().all()
    return render_template('users/list.html', users=users)

@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@require_roles('admin')
def edit_user(user_id):
    user = db.get_or_404(User, user_id)
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role')

        if not username or not email:
            flash("Username and email cannot be empty.", "danger")
            return redirect(url_for('users.edit_user', user_id=user.id))
        
        if role not in ['admin', 'teacher', 'student', 'user']:
            flash("Invalid role selected.", "danger")
            return redirect(url_for('users.edit_user', user_id=user.id))

        existing_user = db.session.execute(
            select(User).where(User.username == username, User.id != user.id)
        ).scalar_one_or_none()
        if existing_user:
            flash("Username is already taken.", "danger")
            return redirect(url_for('users.edit_user', user_id=user.id))
        
        existing_email = db.session.execute(
            select(User).where(User.email == email, User.id != user.id)
        ).scalar_one_or_none()
        if existing_email:
            flash("Email is already taken.", "danger")
            return redirect(url_for('users.edit_user', user_id=user.id))

        user.username = username
        user.email = email
        user.role = role
        db.session.commit()
        
        flash("User updated successfully!", "success")
        return redirect(url_for('users.list_users'))

    return render_template('users/edit.html', user=user)

@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@require_roles('admin')
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    
    if user.id == current_user.id:
        flash("You cannot delete your own account!", "danger")
        return redirect(url_for('users.list_users'))
        
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "success")
    return redirect(url_for('users.list_users'))
