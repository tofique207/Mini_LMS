from flask import Blueprint

students_bp=Blueprint('students',__name__,url_prefix='/students')

@students_bp.route('/')
def student_home():
    return "Student Home Page"