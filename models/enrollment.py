from flask_sqlalchemy import SQLAlchemy
from app import db
from models.enums import EnrollmentType, StudyLevel, SurveyStudyLevel

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.String(100), db.ForeignKey('institution.institution_id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    enrollment_type = db.Column(db.Enum(EnrollmentType), nullable=False)
    study_level = db.Column(db.Enum(StudyLevel), nullable=False)
    survey_study_level = db.Column(db.Enum(SurveyStudyLevel), nullable=False)
    total_enrollment = db.Column(db.Integer, nullable=False)


    institution = db.relationship('Institution', backref=db.backref('enrollments', lazy=True))
