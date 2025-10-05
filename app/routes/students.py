from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Student
from flask_login import login_required

students_bp=Blueprint('students',__name__,url_prefix='/students')

@students_bp.route('/')
@login_required
def student_home():
    students=Student.query.all()
    return render_template('students/list.html')

@students_bp.route('/add',methods=["GET",'POST'])
@login_required
def add_student():
    if request.method=='POST':
        name=request.form.get('name')
        email=request.form.get('email')
        course=request.form.get('course')
        age=request.form.get('age')

        existing_student=Student.query.filter_by(email=email).first()
        if existing_student:
            flash("Student Already Exists")
            return redirect(url_for("students.add_student"))
        
        new_student=Student(name=name, email=email, course=course, age=age)
        db.session.add(new_student)
        db.session.commit()
        flash("Student Added Successfully")
        return redirect(url_for("students.student_home"))
    
    return render_template('students/add.html')