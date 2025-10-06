from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db
from flask_login import login_user, logout_user, login_required

auth_bp=Blueprint('auth',__name__,url_prefix='/auth')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if not user:
            flash("User Does not Exist...Please Register First!!")
            return redirect(url_for('auth.login'))
        
        if not check_password_hash(user.password, password):
            flash("Incorrect Password!!","danger")
            return redirect(url_for('auth.login'))
        
        login_user(user)
        flash("login Successfull!!")
        return redirect(url_for('dashboard.dashboard_home'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been Logged-Out")
    return redirect(url_for('auth.login'))

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