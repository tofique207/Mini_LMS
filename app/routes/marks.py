from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Mark, Student, Course
from app.utils.auth import require_roles

marks_bp = Blueprint('marks', __name__, url_prefix='/marks')

@marks_bp.route('/')
@login_required
@require_roles('admin', 'teacher', 'student')
def list_marks():
    if current_user.role == 'admin':
        stmt = db.select(Mark)
    elif current_user.role == 'teacher':
        stmt = db.select(Mark).join(Course).filter(Course.teacher_id == current_user.id)
    else:  # student
        stmt = db.select(Mark).join(Student).filter(Student.user_id == current_user.id)
        
    marks = db.session.execute(stmt).scalars().all()
    return render_template('marks/list.html', marks=marks)

@marks_bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_roles('admin', 'teacher')
def add_mark():
    if request.method == 'POST':
        try:
            student_id = int(request.form.get('student_id'))
            course_id = int(request.form.get('course_id'))
        except (ValueError, TypeError):
            flash("Invalid student or course selection.", "danger")
            return redirect(url_for('marks.add_mark'))  
        try:
            marks = float(request.form.get('marks', 0))
            total_marks = float(request.form.get('total_marks', 100.0))
        except (ValueError, TypeError):
            flash("Invalid marks value.", "danger")
            return redirect(url_for('marks.add_mark'))
        
        if not (0 <= marks <= total_marks):
            flash("Invalid marks limit.", "danger")
            return redirect(url_for('marks.add_mark'))
            
        existing_mark = db.session.execute(
            db.select(Mark).filter_by(student_id=student_id, course_id=course_id)
        ).scalar_one_or_none()
        
        if existing_mark:
            flash("Mark already exists! Use edit instead.", "warning")
            return redirect(url_for('marks.list_marks'))
            
        new_mark = Mark(
            student_id=student_id,
            course_id=course_id,
            marks=marks,
            total_marks=total_marks,
            recorded_by=current_user.id
        )
        db.session.add(new_mark)
        db.session.commit()
        flash("Mark added successfully!", "success")
        return redirect(url_for('marks.list_marks'))
        
    students_stmt = db.select(Student)
    students = db.session.execute(students_stmt).scalars().all()
    
    if current_user.role == 'admin':
        courses_stmt = db.select(Course)
    else:
        courses_stmt = db.select(Course).filter(Course.teacher_id == current_user.id)
        
    courses = db.session.execute(courses_stmt).scalars().all()
    
    return render_template('marks/add.html', students=students, courses=courses)

@marks_bp.route('/edit/<int:mark_id>', methods=['GET', 'POST'])
@login_required
@require_roles('admin', 'teacher')
def edit_mark(mark_id):
    mark = db.get_or_404(Mark, mark_id)
    
    if current_user.role == 'teacher' and mark.course.teacher_id != current_user.id:
        flash("Unauthorized to edit this mark.", "danger")
        return redirect(url_for('marks.list_marks'))
        
    if request.method == 'POST':
        try:
            marks = float(request.form.get('marks', 0))
            total_marks = float(request.form.get('total_marks', 100.0))
        except (ValueError, TypeError):
            flash("Invalid marks value.", "danger")
            return redirect(url_for('marks.edit_mark', mark_id=mark.id))
        
        if not (0 <= marks <= total_marks):
            flash("Invalid marks limit.", "danger")
            return redirect(url_for('marks.edit_mark', mark_id=mark.id))
            
        mark.marks = marks
        mark.total_marks = total_marks
        db.session.commit()
        
        flash("Mark updated successfully!", "success")
        return redirect(url_for('marks.list_marks'))
        
    return render_template('marks/edit.html', mark=mark)

@marks_bp.route('/delete/<int:mark_id>', methods=['POST'])
@login_required
@require_roles('admin')
def delete_mark(mark_id):
    mark = db.get_or_404(Mark, mark_id)
    db.session.delete(mark)
    db.session.commit()
    flash("Mark deleted successfully!", "success")
    return redirect(url_for('marks.list_marks'))
