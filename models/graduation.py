from flask_sqlalchemy import SQLAlchemy
from app import db

class GraduationCohort(db.Model):
    __tablename__ = 'graduation_cohorts'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    grtype_code = db.Column(db.Integer, nullable=False)
    grtype_label = db.Column(db.String(255), nullable=False)
    section_code = db.Column(db.Integer, nullable=True)
    section_label = db.Column(db.String(255), nullable=True)

    # Relationship to Institution
    institution = db.relationship('Institution', backref=db.backref('graduation_cohorts', lazy=True))

    # Relationship to GraduationStatus
    statuses = db.relationship('GraduationStatus', backref='cohort', lazy=True)

class GraduationStatus(db.Model):
    __tablename__ = 'graduation_statuses'
    id = db.Column(db.Integer, primary_key=True)
    cohort_id = db.Column(db.Integer, db.ForeignKey('graduation_cohorts.id'), nullable=False)
    chrtstat_code = db.Column(db.Integer, nullable=False)
    chrtstat_label = db.Column(db.String(255), nullable=False)
    student_count = db.Column(db.Integer, nullable=False)