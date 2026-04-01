from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Student
from flask_login import login_required, current_user
from app.utils.auth import require_roles
import re

students_bp = Blueprint('students', __name__, url_prefix='/students')

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


# List all students (admin only)
@students_bp.route('/')
@login_required
@require_roles('admin')
def student_home():
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('students/list.html', students=students)


# Add student profile (only for users who are "student" role)
@students_bp.route('/add', methods=["GET", "POST"])
@login_required
@require_roles('student', 'user')
def add_student():
    # Prevent duplicate student profile
    if current_user.student:
        flash("You already created your student profile.", "warning")
        return redirect(url_for("dashboard.dashboard_home"))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        age_raw = request.form.get('age', '').strip()

        # Validate name
        if not name:
            flash("Name is required.", "danger")
            return redirect(url_for("students.add_student"))

        # Validate email
        if not email or not EMAIL_RE.match(email):
            flash("A valid email is required.", "danger")
            return redirect(url_for("students.add_student"))

        # Validate age
        age = None
        if age_raw:
            try:
                age = int(age_raw)
                if age < 0:
                    raise ValueError
            except ValueError:
                flash("Age must be a positive integer.", "danger")
                return redirect(url_for("students.add_student"))

        # Duplicate email check
        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            flash("A student with this email already exists.", "danger")
            return redirect(url_for("students.add_student"))

        # Create student profile linked to this user
        new_student = Student(
            name=name,
            email=email,
            age=age,
            user_id=current_user.id
        )
        db.session.add(new_student)
        db.session.commit()

        if current_user.role == 'user':
            current_user.role = 'student'
            db.session.commit()

        flash("Your student profile has been created!", "success")
        return redirect(url_for("dashboard.dashboard_home"))

    return render_template('students/add.html')


# Update student profile (only for users who are "student" role)
@students_bp.route('/update', methods=["GET", "POST"])
@login_required
@require_roles('student')
def update_student():
    student = current_user.student
    if not student:
        flash("No student profile found. Please create one first.", "warning")
        return redirect(url_for("students.add_student"))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        age_raw = request.form.get('age', '').strip()

        # Validate name
        if not name:
            flash("Name is required.", "danger")
            return redirect(url_for("students.update_student"))

        # Validate email
        if not email or not EMAIL_RE.match(email):
            flash("A valid email is required.", "danger")
            return redirect(url_for("students.update_student"))

        # Validate age
        age = None
        if age_raw:
            try:
                age = int(age_raw)
                if age < 0:
                    raise ValueError
            except ValueError:
                flash("Age must be a positive integer.", "danger")
                return redirect(url_for("students.update_student"))

        # Duplicate email check only if email changed
        if email != student.email:
            existing_student = Student.query.filter_by(email=email).first()
            if existing_student:
                flash("A student with this email already exists.", "danger")
                return redirect(url_for("students.update_student"))

        student.name = name
        student.email = email
        student.age = age
        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for("dashboard.dashboard_home"))

    return render_template('students/update.html', student=student)
