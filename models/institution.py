from flask_sqlalchemy import SQLAlchemy
from app import db
from .enums import (InstitutionControl, InstitutionLevel, HighestDegree,
                   InstitutionLocale, InstitutionStatus, Pset4Flag,
                   InstitutionCategory, InstitutionSizeClassification,
                   CarnegieClassification)


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    alias = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip = db.Column(db.String(100), nullable=True)
    web_url = db.Column(db.String(100), nullable=True)
    county = db.Column(db.String(100), nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    title_iv_eligible = db.Column(db.Boolean, nullable=True)
    admin_url = db.Column(db.String(100), nullable=True)
    financial_aid_url = db.Column(db.String(100), nullable=True)
    application_url = db.Column(db.String(100), nullable=True)
    net_price_calculator_url = db.Column(db.String(100), nullable=True)
    right_to_know_url = db.Column(db.String(100), nullable=True)
    disability_services_url = db.Column(db.String(100), nullable=True)
    control = db.Column(db.Enum(InstitutionControl), nullable=True)
    level = db.Column(db.Enum(InstitutionLevel), nullable=True)
    highest_degree = db.Column(db.Enum(HighestDegree), nullable=True)
    undergraduate_degree_offered = db.Column(db.Boolean, nullable=True)
    graduate_degree_offered = db.Column(db.Boolean, nullable=True)
    hbcu = db.Column(db.Boolean, nullable=True)
    medical_school = db.Column(db.Boolean, nullable=True)
    locale = db.Column(db.Enum(InstitutionLocale), nullable=True)
    open_to_public = db.Column(db.Boolean, nullable=True)
    status = db.Column(db.Enum(InstitutionStatus), nullable=True)
    pset4_flag = db.Column(db.Enum(Pset4Flag), nullable=True)
    institution_category = db.Column(db.Enum(InstitutionCategory), nullable=True)
    size_classification = db.Column(db.Enum(InstitutionSizeClassification), nullable=True)
    carnegie_classification = db.Column(db.Enum(CarnegieClassification), nullable=True)