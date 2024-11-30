from flask_sqlalchemy import SQLAlchemy
from app import db
from .enums import AwardLevel

class Completitions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.String(100), db.ForeignKey('institution.institution_id'), nullable=False)
    program_classification_code = db.Column(db.String(10), nullable=False)
    program_classification = db.Column(db.String(100), nullable=False)
    first_major = db.Column(db.String(100), nullable=False)
    award_level_code = db.Column(db.Enum(AwardLevel), nullable=False)
    total_completions = db.Column(db.Integer, nullable=False)
    
    institution = db.relationship('Institution', backref=db.backref('completitions', lazy=True))
