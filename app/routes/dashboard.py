from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Student, Course, Enrollment, Mark, Attendance

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def dashboard_home():
    # --- Admin Dashboard ---
    if current_user.role == 'admin':
        total_students = db.session.scalar(db.select(db.func.count()).select_from(Student))
        total_courses = db.session.scalar(db.select(db.func.count()).select_from(Course))
        total_enrollments = db.session.scalar(db.select(db.func.count()).select_from(Enrollment))

        recent_enrollments = db.session.scalars(
            db.select(Enrollment).order_by(Enrollment.enrolled_on.desc()).limit(5)
        ).all()

        return render_template(
            'dashboard/admin.html',
            total_students=total_students,
            total_courses=total_courses,
            total_enrollments=total_enrollments,
            recent_enrollments=recent_enrollments
        )

    # --- Teacher Dashboard ---
    if current_user.role == 'teacher':
        # Courses assigned to teacher
        courses = db.session.scalars(
            db.select(Course).filter_by(teacher_id=current_user.id)
        ).all()

        course_ids = [c.id for c in courses]

        # Handle empty case safely
        if course_ids:
            enrollments = db.session.scalars(
                db.select(Enrollment).filter(Enrollment.course_id.in_(course_ids))
            ).all()
        else:
            enrollments = []

        # Unique students
        student_ids = list({e.student_id for e in enrollments})

        if student_ids:
            students = db.session.scalars(
                db.select(Student).filter(Student.id.in_(student_ids))
            ).all()
        else:
            students = []

        # Precompute student count per course (IMPORTANT)
        course_student_count = {}
        for c in courses:
            course_student_count[c.id] = sum(
                1 for e in enrollments if e.course_id == c.id
            )

        # Marks
        marks = db.session.scalars(
            db.select(Mark).filter_by(recorded_by=current_user.id)
        ).all()

        # Attendance
        attendance_records = db.session.scalars(
            db.select(Attendance).filter_by(recorded_by=current_user.id)
        ).all()

        return render_template(
            'dashboard/teacher.html',
            courses=courses,
            students=students,
            marks=marks,
            attendance_records=attendance_records,
            course_student_count=course_student_count
        )

    # --- Student Dashboard ---
    student_profile = db.session.scalars(
        db.select(Student).filter_by(user_id=current_user.id)
    ).first()

    if student_profile:
        student_enrollments = db.session.scalars(
            db.select(Enrollment).filter_by(student_id=student_profile.id)
        ).all()
        return render_template(
            'dashboard/student.html',
            student=student_profile,
            enrollments=student_enrollments
        )
    else:
        return render_template('dashboard/student_no_profile.html')