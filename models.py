from enum import IntEnum, Enum
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

class InstitutionLocale(IntEnum):
    UNKNOWN = -3
    
    # City categories
    CITY_LARGE = 11      # Territory inside urbanized area, principal city with population ≥250,000
    CITY_MIDSIZE = 12    # Territory inside urbanized area, principal city with 100,000-250,000 population
    CITY_SMALL = 13      # Territory inside urbanized area, principal city with <100,000 population
    
    # Suburb categories
    SUBURB_LARGE = 21    # Outside principal city, inside urbanized area with ≥250,000 population
    SUBURB_MIDSIZE = 22  # Outside principal city, inside urbanized area with 100,000-250,000 population
    SUBURB_SMALL = 23    # Outside principal city, inside urbanized area with <100,000 population
    
    # Town categories
    TOWN_FRINGE = 31    # Territory ≤10 miles from urbanized area
    TOWN_DISTANT = 32   # Territory >10 and ≤35 miles from urbanized area
    TOWN_REMOTE = 33    # Territory >35 miles from urbanized area
    
    # Rural categories
    RURAL_FRINGE = 41   # Rural territory ≤5 miles from urbanized area or ≤2.5 miles from urban cluster
    RURAL_DISTANT = 42  # Rural territory >5 but ≤25 miles from urbanized area or >2.5 but ≤10 miles from urban cluster
    RURAL_REMOTE = 43   # Rural territory >25 miles from urbanized area and >10 miles from urban cluster

class InstitutionStatus(str, Enum):
    ACTIVE = 'A'              # Open/active institution
    NEW = 'N'                 # Institution opened in current year
    CLOSED_WITH_DATA = 'M'    # Closed in current year but has previous year's data
    RESTORED = 'R'            # Previously inactive institution restored in current year

class Pset4Flag(IntEnum):
    UNKNOWN = -3
    NOT_IN_UNIVERSE = 0
    TITLE_IV_CURRENT = 1      # Title IV, current primarily postsecondary
    TITLE_IV_NOT_PRIMARY = 2  # Title IV, not primarily postsecondary
    TITLE_IV_NOT_ACTIVE = 3   # Title IV, not active in current year
    NON_TITLE_IV_CURRENT = 4  # Non-Title IV, current primarily postsecondary
    MILITARY_ACADEMY = 5      # Military academies (including Coast Guard)
    ADMIN_UNIT = 9           # Administrative units

class InstitutionCategory(IntEnum):
    UNKNOWN = -3
    GRADUATE_NO_UNDERGRAD = 1
    PRIMARILY_BACCALAUREATE = 2
    NOT_PRIMARILY_BACCALAUREATE = 3
    ASSOCIATES_AND_CERTIFICATES = 4
    ABOVE_BACCALAUREATE = 5
    SUB_BACCALAUREATE = 6

class InstitutionSizeClassification(IntEnum):
    UNKNOWN = -3
    
    # Two-year institutions
    TWO_YEAR_VERY_SMALL = 11  # FTE enrollment of fewer than 500 students
    TWO_YEAR_SMALL = 12       # FTE enrollment of 500-1,999 students
    TWO_YEAR_MEDIUM = 13      # FTE enrollment of 2,000-4,999 students
    TWO_YEAR_LARGE = 14       # FTE enrollment of 5,000-9,999 students
    TWO_YEAR_VERY_LARGE = 15  # FTE enrollment of at least 10,000 students

    # Four-year institutions - Very Small
    FOUR_YEAR_VERY_SMALL_NONRES = 21    # <1,000 students, <25% live on campus
    FOUR_YEAR_VERY_SMALL_RES = 22       # <1,000 students, 25-49% live on campus
    FOUR_YEAR_VERY_SMALL_HIGHLY_RES = 23 # <1,000 students, ≥50% live on campus

    # Four-year institutions - Small
    FOUR_YEAR_SMALL_NONRES = 31         # 1,000-2,999 students, <25% live on campus
    FOUR_YEAR_SMALL_RES = 32            # 1,000-2,999 students, 25-49% live on campus
    FOUR_YEAR_SMALL_HIGHLY_RES = 33     # 1,000-2,999 students, ≥50% live on campus

    # Four-year institutions - Medium
    FOUR_YEAR_MEDIUM_NONRES = 41        # 3,000-9,999 students, <25% live on campus
    FOUR_YEAR_MEDIUM_RES = 42           # 3,000-9,999 students, 25-49% live on campus
    FOUR_YEAR_MEDIUM_HIGHLY_RES = 43    # 3,000-9,999 students, ≥50% live on campus

    # Four-year institutions - Large
    FOUR_YEAR_LARGE_NONRES = 51         # ≥10,000 students, <25% live on campus
    FOUR_YEAR_LARGE_RES = 52            # ≥10,000 students, 25-49% live on campus
    FOUR_YEAR_LARGE_HIGHLY_RES = 53     # ≥10,000 students, ≥50% live on campus

    # Exclusively graduate/professional
    EXCLUSIVELY_GRADUATE = 60            # No undergraduate enrollment

class CarnegieClassification(IntEnum):
    UNKNOWN = -3
    ASSOC_PUB_R_S = 1
    ASSOC_PUB_R_M = 2
    ASSOC_PUB_R_L = 3
    ASSOC_PUB_S_SC = 4
    ASSOC_PUB_S_MC = 5
    ASSOC_PUB_U_SC = 6
    ASSOC_PUB_U_MC = 7
    ASSOC_PUB_SPEC = 8
    ASSOC_PRIV_NFP = 9
    ASSOC_PRIV_FP = 10
    TRIBAL = 11
    RU_VH = 15
    RU_H = 16
    DRU = 17
    MASTERS_L = 18
    MASTERS_M = 19
    MASTERS_S = 20
    BAC_AS = 21
    BAC_DIVERSE = 22
    BAC_ASSOC = 23
    SPEC_FAITH = 24
    SPEC_MEDICAL = 25
    SPEC_HEALTH = 26
    SPEC_ENGG = 27
    SPEC_TECH = 28
    SPEC_BUS = 29
    SPEC_ARTS = 30
    SPEC_LAW = 31
    SPEC_OTHER = 32

class StandardizedAnswer(IntEnum):
    NOT_REPORTED = -1
    NOT_APPLICABLE = -2
    IMPLIED_NO = 0
    YES = 1
    NO = 2

class MealPlanType(IntEnum):
    NOT_REPORTED = -1
    NOT_APPLICABLE = -2
    NO = 3                    # No meal plan offered
    FIXED = 1                 # Fixed number of meals in maximum meal plan
    VARIABLE = 2              # Number of meals per week can vary

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

class Institutional_Attributes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.String(100), db.ForeignKey('institution.institution_id'), nullable=False)
    advance_placement_credits_accepted = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    credit_for_any_credits = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    rotc_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    rotc_army_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    rotc_navy_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    rotc_airforce_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    rotc_marine_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    study_abroad_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    weekend_college_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    undergraduate_teacher_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    specialized_teacher_preparation_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    teacher_certification_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    no_teacher_certification_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    transition_program_for_disabled_students_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    academic_counseling_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    employment_services_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    placement_services_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    oncampus_daycare_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    no_student_services_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    physical_library_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    printed_materials_library_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    online_library_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    trained_librarian_available = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    no_library_services_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    alternative_tuition_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    tuition_guaranteed_plan_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    tuition_payment_plan_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    other_alternative_tuition_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    
    required_live_on_campus = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    oncampus_housing_offered = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    
    disabled_students_percentage = db.Column(db.Float, nullable=True)
    oncampus_capacity = db.Column(db.Integer, nullable=True)
    
    meal_plan_offered = db.Column(db.Enum(MealPlanType), nullable=True)
    number_of_meals_per_week = db.Column(db.Integer, nullable=True)
    housing_charge_per_year = db.Column(db.Integer, nullable=True)
    meal_plan_charge_per_year = db.Column(db.Integer, nullable=True)
    combined_charge_per_year = db.Column(db.Integer, nullable=True)
    undergraduate_application_fee = db.Column(db.Integer, nullable=True)
    graduate_application_fee = db.Column(db.Integer, nullable=True)

    member_of_naa = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    member_of_ncaa = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    member_of_naia = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    member_of_njcaa = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    member_of_nscaa = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    member_of_nccaa = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    member_of_other_athletic_association = db.Column(db.Enum(StandardizedAnswer), nullable=True)
    member_of_ncaaa_football = db.Column(db.Enum(StandardizedAnswer), nullable=True)

    # Define relationship
    institution = db.relationship('Institution', backref=db.backref('institutional_attributes', lazy=True))
