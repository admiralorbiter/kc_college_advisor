from enum import IntEnum, Enum

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

class AwardLevel(IntEnum):
    CERTIFICATE_UNDER_1_YEAR = 20      # Certificates of less than 12 weeks
    CERTIFICATE_1_YEAR = 21            # Certificates of at least 12 weeks but less than 1 year
    CERTIFICATE_2_YEAR = 2             # Certificates of at least 1 but less than 2 years
    CERTIFICATE_4_YEAR = 4             # Certificates of at least 2 but less than 4 years
    ASSOCIATES = 3                     # Associate's degree
    BACHELORS = 5                      # Bachelor's degree
    POST_BACCALAUREATE = 6             # Postbaccalaureate certificate
    MASTERS = 7                        # Master's degree
    POST_MASTERS = 8                   # Post-master's certificate
    DOCTORATE_RESEARCH = 17            # Doctor's degree - research/scholarship
    DOCTORATE_PROFESSIONAL = 18        # Doctor's degree - professional practice
    DOCTORATE_OTHER = 19               # Doctor's degree - other

class EnrollmentType(IntEnum):
    # All Students Categories
    ALL_STUDENTS_TOTAL = 1
    ALL_STUDENTS_UNDERGRAD = 2
    ALL_STUDENTS_UNDERGRAD_DEGREE_SEEKING = 3
    ALL_STUDENTS_UNDERGRAD_DEGREE_SEEKING_FIRST_TIME = 4
    ALL_STUDENTS_UNDERGRAD_OTHER = 5  # Added: Other first-year undergraduates
    ALL_STUDENTS_UNDERGRAD_DEGREE_SEEKING_TRANSFER = 19
    ALL_STUDENTS_UNDERGRAD_DEGREE_SEEKING_CONTINUING = 20
    ALL_STUDENTS_UNDERGRAD_NON_DEGREE = 11
    ALL_STUDENTS_GRADUATE = 12

    # Full-time Students
    FULL_TIME_TOTAL = 21
    FULL_TIME_UNDERGRAD = 22
    FULL_TIME_UNDERGRAD_DEGREE_SEEKING = 23
    FULL_TIME_UNDERGRAD_DEGREE_SEEKING_FIRST_TIME = 24
    FULL_TIME_UNDERGRAD_OTHER = 25  # Added: Other full-time first-year undergraduates
    FULL_TIME_UNDERGRAD_DEGREE_SEEKING_TRANSFER = 39
    FULL_TIME_UNDERGRAD_DEGREE_SEEKING_CONTINUING = 40
    FULL_TIME_UNDERGRAD_NON_DEGREE = 31
    FULL_TIME_GRADUATE = 32

    # Part-time Students
    PART_TIME_TOTAL = 41
    PART_TIME_UNDERGRAD = 42
    PART_TIME_UNDERGRAD_DEGREE_SEEKING = 43
    PART_TIME_UNDERGRAD_DEGREE_SEEKING_FIRST_TIME = 44
    PART_TIME_UNDERGRAD_OTHER = 45  # Added: Other part-time first-year undergraduates
    PART_TIME_UNDERGRAD_DEGREE_SEEKING_TRANSFER = 59
    PART_TIME_UNDERGRAD_DEGREE_SEEKING_CONTINUING = 60
    PART_TIME_UNDERGRAD_NON_DEGREE = 51
    PART_TIME_GRADUATE = 52

class StudyLevel(IntEnum):
    NOT_APPLICABLE = -2
    UNDERGRADUATE = 1
    GRADUATE = 3
    GENERATED_TOTAL = 999

class SurveyStudyLevel(IntEnum):
    UNDERGRADUATE = 1  # Students in 4/5-year bachelor's, associate's, or vocational programs
    GRADUATE = 3      # Students with bachelor's degree taking postbaccalaureate courses
