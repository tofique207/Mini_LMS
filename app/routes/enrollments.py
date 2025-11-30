from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from app import db
from app.models import Enrollment, Student, Course
from flask_login import login_required, current_user
from app.utils.auth import require_roles

enroll_bp = Blueprint('enrollments', __name__, url_prefix='/enrollments')


# ============================
#   UI ROUTES (ADMIN ONLY)
# ============================

@enroll_bp.route('/create', methods=['GET', 'POST'])
@login_required
@require_roles('admin')
def create_enrollment_ui():
    students = Student.query.order_by(Student.created_at.desc()).all()
    courses = Course.query.order_by(Course.created_at.desc()).all()

    if request.method == 'POST':
        # Validate IDs
        try:
            student_id = int(request.form.get('student_id'))
            course_id = int(request.form.get('course_id'))
        except (ValueError, TypeError):
            flash('Invalid student or course selection.', 'danger')
            return redirect(url_for('enrollments.create_enrollment_ui'))

        role = request.form.get('role', 'student')
        if role not in ['student', 'TA']:
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('enrollments.create_enrollment_ui'))

        # Check existence
        student = Student.query.get(student_id)
        course = Course.query.get(course_id)
        if not student or not course:
            flash('Student or course does not exist.', 'danger')
            return redirect(url_for('enrollments.create_enrollment_ui'))

        # Check duplicates
        existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if existing:
            flash('Student is already enrolled in this course.', 'danger')
            return redirect(url_for('enrollments.create_enrollment_ui'))

        # Create enrollment
        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            role=role
        )
        db.session.add(enrollment)
        db.session.commit()

        flash('Enrollment created successfully!', 'success')
        return redirect(url_for('enrollments.list_enrollments_ui'))

    return render_template('enrollments/create.html', students=students, courses=courses)



@enroll_bp.route('/list', methods=['GET'])
@login_required
@require_roles('admin')
def list_enrollments_ui():
    page = request.args.get('page', 1, type=int)
    limit = 10

    paginated = Enrollment.query.order_by(Enrollment.enrolled_on.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    enrollments = paginated.items

    return render_template('enrollments/list.html', enrollments=enrollments, paginated=paginated)



@enroll_bp.route('/update/<int:enrollment_id>', methods=['GET', 'POST'])
@login_required
@require_roles('admin')
def update_enrollment_ui(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)

    if request.method == 'POST':
        role = request.form.get('role')
        if role not in ['student', 'TA']:
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('enrollments.update_enrollment_ui', enrollment_id=enrollment_id))

        enrollment.role = role
        db.session.commit()

        flash('Enrollment updated successfully!', 'success')
        return redirect(url_for('enrollments.list_enrollments_ui'))

    return render_template('enrollments/update.html', enrollment=enrollment)



@enroll_bp.route('/delete/<int:enrollment_id>', methods=['POST'])
@login_required
@require_roles('admin')
def delete_enrollment_ui(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)

    db.session.delete(enrollment)
    db.session.commit()

    flash('Enrollment deleted successfully!', 'success')
    return redirect(url_for('enrollments.list_enrollments_ui'))


# ============================
#   API ROUTES
# ============================

# ADMIN: Create enrollment
@enroll_bp.route('/api', methods=['POST'])
@login_required
@require_roles('admin')
def create_enrollment_api():
    data = request.get_json() or {}

    student_id = data.get('student_id')
    course_id = data.get('course_id')
    role = data.get('role', 'student')

    # Validate role
    if role not in ['student', 'TA']:
        return jsonify({'error': 'Invalid role'}), 400

    student = Student.query.get(student_id)
    course = Course.query.get(course_id)

    if not student or not course:
        return jsonify({'error': 'Student or course does not exist'}), 404

    existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing:
        return jsonify({'error': 'Student already enrolled'}), 400

    enrollment = Enrollment(student_id=student_id, course_id=course_id, role=role)
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({
        'message': 'Enrollment created',
        'enrollment': {
            'id': enrollment.id,
            'student': student.name,
            'course': course.course_name,
            'role': role,
            'enrolled_on': enrollment.enrolled_on.isoformat()
        }
    }), 201


# ADMIN: Update enrollment
@enroll_bp.route('/api/<int:enrollment_id>', methods=['PUT'])
@login_required
@require_roles('admin')
def update_enrollment_api(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    data = request.get_json() or {}

    role = data.get('role')
    if role not in ['student', 'TA']:
        return jsonify({'error': 'Invalid role'}), 400

    enrollment.role = role
    db.session.commit()

    return jsonify({'message': 'Enrollment updated'}), 200


# ADMIN: Delete enrollment
@enroll_bp.route('/api/<int:enrollment_id>', methods=['DELETE'])
@login_required
@require_roles('admin')
def delete_enrollment_api(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({'message': 'Enrollment deleted'}), 200


# STUDENT: View their own enrollments
@enroll_bp.route('/api/me', methods=['GET'])
@login_required
@require_roles('student')
def get_my_enrollments_api():
    student = current_user.student
    if not student:
        return jsonify({'error': 'No student profile found'}), 404

    enrollments = Enrollment.query.filter_by(student_id=student.id).all()

    return jsonify([
        {
            'id': e.id,
            'course': e.course.course_name,
            'role': e.role,
            'enrolled_on': e.enrolled_on.isoformat()
        }
        for e in enrollments
    ]), 200
