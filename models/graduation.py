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

class IPEDSGraduationMetrics(db.Model):
    __tablename__ = 'ipeds_graduation_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)  # UNITID
    
    # Bachelor's Degree Metrics
    bachelors_revised_cohort = db.Column(db.Integer)          # BAREVCT
    bachelors_completed_100pct = db.Column(db.Integer)        # BANC100
    bachelors_completed_150pct = db.Column(db.Integer)        # BANC150
    bachelors_completed_200pct = db.Column(db.Integer)        # BANC200
    bachelors_still_enrolled = db.Column(db.Integer)          # BASTEND
    
    # Bachelor's Graduation Rates
    bachelors_grad_rate_100 = db.Column(db.Float)            # BAGR100
    bachelors_grad_rate_150 = db.Column(db.Float)            # BAGR150
    bachelors_grad_rate_200 = db.Column(db.Float)            # BAGR200
    
    # Less than 4-year Degree Metrics
    certificate_revised_cohort = db.Column(db.Integer)        # L4REVCT
    certificate_completed_100pct = db.Column(db.Integer)      # L4NC100
    certificate_completed_150pct = db.Column(db.Integer)      # L4NC150
    certificate_completed_200pct = db.Column(db.Integer)      # L4NC200
    certificate_still_enrolled = db.Column(db.Integer)        # L4STEND
    
    # Less than 4-year Graduation Rates
    certificate_grad_rate_100 = db.Column(db.Float)          # L4GR100
    certificate_grad_rate_150 = db.Column(db.Float)          # L4GR150
    certificate_grad_rate_200 = db.Column(db.Float)          # L4GR200
    
    # Relationships
    institution = db.relationship('Institution', backref=db.backref('ipeds_graduation_metrics', lazy=True))
    
    