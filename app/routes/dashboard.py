from flask import Blueprint
from flask_login import login_required, current_user
from flask import render_template

dashboard_bp=Blueprint('dashboard',__name__,url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard_home():
    return render_template('dashboard/home.html')