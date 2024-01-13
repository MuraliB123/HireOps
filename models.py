from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class Employees(db.Model):
    emp_id = db.Column(db.Integer, primary_key=True)
class skills(db.Model):
    __tablename__ = 'skills'
    employee_id = db.Column(db.Integer, nullable=True,primary_key=True)
    SKILLS = db.Column(db.String(109), nullable=True)
class EmployeeDetails(db.Model):
    __tablename__ = 'employee_details'
    
    EMPLOYEE_ID = db.Column(db.Integer, primary_key=True)
    EMPLOYEE_NAME = db.Column(db.String(10), nullable=True)
    MAIL = db.Column(db.String(17), nullable=True)
    CREDIT_SCORE = db.Column(db.DECIMAL(4, 2), nullable=True)
    PROFILE = db.Column(db.String(9), nullable=True)