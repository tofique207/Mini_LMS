from flask import Blueprint

courses_bp=Blueprint('courses',__name__,url_prefix='/courses')

@courses_bp.route('/')
def courses_home():
    return "Courses Home Page"