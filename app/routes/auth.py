from flask import Blueprint

auth_bp=Blueprint('auth',__name__,url_prefix='/auth')

@auth_bp.route('/')
def login():
    return 'Login Page'