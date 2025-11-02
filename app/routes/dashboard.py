from flask import Blueprint
from flask_login import login_required, current_user
from flask import render_template
from app.models import Student

dashboard_bp=Blueprint('dashboard',__name__,url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard_home():
    student = Student.query.filter_by(user_id=current_user.id).first()
    return render_template('dashboard/home.html')