from flask import Blueprint, request, jsonify
from app import db
from app.models import Enrollment, Student, Course

enroll_bp = Blueprint('enrollments', __name__, url_prefix='/enrollments')

@enroll_bp.route('', methods=['POST'])
def create_enrollment():
    data=request.get_json()
    student_id=data.get('student_id')
    course_id=data.get('course_id')
    role=data.get('role','student')

    if role not in ['student', 'TA']:
        return jsonify({'error': 'Invalid role'}), 400

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student does not exist'}), 404

    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course does not exist'}), 404
    
    try:
        student_id = int(student_id)
        course_id = int(course_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'student_id and course_id must be integers'}), 400

    # Check for duplicate enrollment
    existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing:
        return jsonify({'error': 'Student is already enrolled in this course'}), 400
    
    enrollment = Enrollment(student_id=student_id, course_id=course_id, role=role)
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({
        'message': 'Enrollment created successfully',
        'enrollment': {
            'id': enrollment.id,
            'student': student.name,
            'course': course.course_name,
            'role': enrollment.role,
            'enrolled_on': enrollment.enrolled_on.isoformat()
        }
    }), 201

@enroll_bp.route('', methods=['GET'])
def list_enrollments():
    student_id = request.args.get('student_id', type=int)
    course_id = request.args.get('course_id', type=int)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    query = Enrollment.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    if course_id:
        query = query.filter_by(course_id=course_id)

    paginated =  query.paginate(page=page, per_page=limit, error_out=False)
    enrollments = paginated.items

    result = []
    for e in enrollments:
        result.append({
            'id': e.id,
            'student': e.student.name,
            'course': e.course.course_name,
            'role': e.role,
            'enrolled_on': e.enrolled_on.isoformat()
        })

    return jsonify({
        'page': page,
        'limit': limit,
        'total': paginated.total,
        'pages': paginated.pages,
        'enrollments': result
    }), 200

@enroll_bp.route('/<int:enrollment_id>', methods=['PUT'])
def update_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    data = request.get_json()
    role = data.get('role')
    if role:
        if role not in ['student', 'TA']:
            return jsonify({'error': 'Invalid role'}), 400
        enrollment.role = role

    db.session.commit()

    return jsonify({
        'message': 'Enrollment updated successfully',
        'enrollment': {
            'id': enrollment.id,
            'student': enrollment.student.name,
            'course': enrollment.course.course_name,
            'role': enrollment.role,
            'enrolled_on': enrollment.enrolled_on.isoformat()
        }
    }), 200

@enroll_bp.route('/<int:enrollment_id>', methods=['DELETE'])
def delete_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    db.session.delete(enrollment)
    db.session.commit()

    return jsonify({
        'message': 'Enrollment deleted successfully',
        'enrollment_id': enrollment_id           
    }), 200