from enum import IntEnum
from flask_sqlalchemy import SQLAlchemy
from app import db

class InstitutionLevel(IntEnum):
    UNKNOWN = -3
    FOUR_YEAR = 1
    TWO_YEAR = 2
    LESS_THAN_TWO_YEAR = 3

class InstitutionControl(IntEnum):
    UNKNOWN = -3
    PUBLIC = 1
    PRIVATE_NONPROFIT = 2
    PRIVATE_FORPROFIT = 3

class HighestDegree(IntEnum):
    NOT_AVAILABLE = -3
    NOT_APPLICABLE = -2
    NONE = 0
    LESS_THAN_ONE_YEAR = 1
    ONE_TO_TWO_YEARS = 2
    ASSOCIATES = 3
    TWO_TO_FOUR_YEARS = 4
    BACHELORS = 5
    POST_BACCALAUREATE = 6
    MASTERS = 7
    POST_MASTERS = 8
    DOCTORATE = 9

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
