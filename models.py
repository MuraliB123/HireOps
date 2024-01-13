from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class Employees(db.Model):
    emp_id = db.Column(db.Integer, primary_key=True)
class skills(db.Model):
    __tablename__ = 'skills'
    employee_id = db.Column(db.Integer, nullable=True,primary_key=True)
    SKILLS = db.Column(db.String(109), nullable=True)