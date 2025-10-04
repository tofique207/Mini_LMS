from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db
from flask_login import login_user, logout_user, login_required

auth_bp=Blueprint('auth',__name__,url_prefix='/auth')

@auth_bp.route('/')
def login():
    return 'Login Page'

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method== 'POST':
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')

        user_exists= User.query.filter_by(email=email).first()
        if user_exists:
            flash("Email ALready Exixts!!")
            return redirect(url_for('auth.register'))
        
        hashed_password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        new_user=User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successfull!!...Please Login!!")
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')