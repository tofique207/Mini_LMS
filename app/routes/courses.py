from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Course
from flask_login import login_required, current_user
from functools import wraps

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

# Admin-only access decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash("You do not have permission to access this page!", "danger")
            return redirect(url_for('courses.list_courses'))
        return f(*args, **kwargs)
    return decorated_function

# List all courses
@courses_bp.route('/')
@login_required
def list_courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('courses/list.html', courses=courses)

# Add a new course (admin only)
@courses_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Course name is required!', 'danger')
            return redirect(url_for('courses.add_course'))

        existing_course = Course.query.filter_by(course_name=name).first()
        if existing_course:
            flash('Course already exists!', 'warning')
            return redirect(url_for('courses.add_course'))

        new_course = Course(course_name=name, description=description)
        db.session.add(new_course)
        db.session.commit()
        flash('Course added successfully!', 'success')
        return redirect(url_for('courses.list_courses'))

    return render_template('courses/add.html')

# Edit a course (admin only)
@courses_bp.route('/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        course_name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not course_name:
            flash('Course name cannot be empty!', 'danger')
            return redirect(url_for('courses.edit_course', course_id=course.id))

        course.course_name = course_name
        course.description = description
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('courses.list_courses'))

    return render_template('courses/edit.html', course=course)

# Delete a course (admin only)
@courses_bp.route('/delete/<int:course_id>', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('courses.list_courses'))
