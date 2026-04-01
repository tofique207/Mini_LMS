from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Attendance, Student, Course
from app.utils.auth import require_roles

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/')
@login_required
@require_roles('admin', 'teacher', 'student')
def list_attendance():
    if current_user.role == 'admin':
        stmt = db.select(Attendance)
    elif current_user.role == 'teacher':
        stmt = db.select(Attendance).join(Course).filter(Course.teacher_id == current_user.id)
    else:
        stmt = db.select(Attendance).join(Student).filter(Student.user_id == current_user.id)
        
    records = db.session.scalars(stmt).all()
    return render_template('attendance/list.html', records=records)

@attendance_bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_roles('admin', 'teacher')
def add_attendance():
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        course_id = request.form.get('course_id', type=int)
        attended = request.form.get('attended', type=int)
        total_classes = request.form.get('total_classes', type=int)

        if attended is None or total_classes is None or not (0 <= attended <= total_classes):
            flash("Invalid attendance values.", "danger")
            return redirect(url_for('attendance.list_attendance'))

        existing = db.session.execute(
            db.select(Attendance).filter_by(student_id=student_id, course_id=course_id)
        ).scalar_one_or_none()

        if existing:
            flash("Attendance already exists! Use edit instead.", "warning")
            return redirect(url_for('attendance.list_attendance'))

        attendance = Attendance(
            student_id=student_id,
            course_id=course_id,
            attended=attended,
            total_classes=total_classes,
            recorded_by=current_user.id
        )
        db.session.add(attendance)
        db.session.commit()
        
        flash("Attendance added successfully!", "success")
        return redirect(url_for('attendance.list_attendance'))

    # GET request
    students = db.session.scalars(db.select(Student)).all()
    if current_user.role == 'admin':
        courses = db.session.scalars(db.select(Course)).all()
    else:
        courses = db.session.scalars(db.select(Course).filter_by(teacher_id=current_user.id)).all()

    return render_template('attendance/add.html', students=students, courses=courses)

@attendance_bp.route('/edit/<int:attendance_id>', methods=['GET', 'POST'])
@login_required
@require_roles('admin', 'teacher')
def edit_attendance(attendance_id):
    attendance = db.get_or_404(Attendance, attendance_id)
    
    if current_user.role == 'teacher' and attendance.course.teacher_id != current_user.id:
        flash("You are not authorized to edit this attendance record.", "danger")
        return redirect(url_for('attendance.list_attendance'))

    if request.method == 'POST':
        attended = request.form.get('attended', type=int)
        total_classes = request.form.get('total_classes', type=int)

        if attended is None or total_classes is None or not (0 <= attended <= total_classes):
            flash("Invalid attendance values.", "danger")
            return redirect(url_for('attendance.list_attendance'))

        attendance.attended = attended
        attendance.total_classes = total_classes
        db.session.commit()
        
        flash("Attendance updated successfully!", "success")
        return redirect(url_for('attendance.list_attendance'))

    # GET request
    return render_template('attendance/edit.html', attendance=attendance)

@attendance_bp.route('/delete/<int:attendance_id>', methods=['POST'])
@login_required
@require_roles('admin')
def delete_attendance(attendance_id):
    attendance = db.get_or_404(Attendance, attendance_id)
    db.session.delete(attendance)
    db.session.commit()
    flash("Attendance deleted successfully!", "success")
    return redirect(url_for('attendance.list_attendance'))
