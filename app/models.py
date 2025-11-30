from app import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    student = db.relationship('Student', back_populates='user', uselist=False) #one-to-one relation with student
    role = db.Column(db.String(20), default='user')
    def __repr__(self):
        return f"<User {self.username}>"


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', back_populates='student')

    enrollments = db.relationship(
        'Enrollment',
        back_populates='student',
        cascade='all, delete-orphan'
    )
    courses = db.relationship(
        'Course',
        secondary='enrollment',
        viewonly=True
    )
    def __repr__(self):
        return f"<Student {self.name}>"

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_on = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='student')

    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

    def __repr__(self):
        return f"<Enrollment student={self.student_id} course={self.course_id}>"


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship with Enrollment
    enrollments = db.relationship(
        'Enrollment',
        back_populates='course',
        cascade='all, delete-orphan'
    )
    # Students enrolled in the course (read-only)
    students = db.relationship(
        'Student',
        secondary='enrollment',
        viewonly=True
    )
    def __repr__(self):
        return f"<Course {self.title}>"
