import re
from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
import pandas as pd
import csv
import io
import os
from models.classification_codes import CLASSIFICATION_CODES
from models.enums import *
from models.graduation import GraduationCohort, GraduationStatus, IPEDSGraduationMetrics
from models.institution import Institution
from models.institutional_attributes import Institutional_Attributes
from models.completitions import Completitions

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/colleges', methods=['GET'])
def colleges():
    sort_by = request.args.get('sort', 'name')
    direction = request.args.get('direction', 'asc')
    name_search = request.args.get('name_search', '').strip()
    location_search = request.args.get('location_search', '').strip()
    
    # Toggle sort direction
    sort_direction = 'desc' if direction == 'asc' else 'asc'
    
    # Start with base query
    query = Institution.query.filter(Institution.state.in_(['MO', 'KS']))
    
    # Add eager loading for both graduation cohorts and IPEDS metrics
    query = query.options(
        db.joinedload(Institution.graduation_cohorts).joinedload(GraduationCohort.statuses),
        db.joinedload(Institution.ipeds_graduation_metrics)
    )
    
    # Apply search filters
    if name_search:
        query = query.filter(
            db.or_(
                Institution.name.ilike(f'%{name_search}%'),
                Institution.alias.ilike(f'%{name_search}%')
            )
        )
    
    if location_search:
        query = query.filter(
            db.or_(
                Institution.city.ilike(f'%{location_search}%'),
                Institution.state.ilike(f'%{location_search}%'),
                Institution.county.ilike(f'%{location_search}%')
            )
        )
    
    # Get results based on non-completion rate sorting
    if sort_by != 'completion_rate':
        sort_column = getattr(Institution, sort_by)
        if direction == 'desc':
            sort_column = sort_column.desc()
        institutions = query.order_by(sort_column).all()
    else:
        institutions = query.all()  # Get all results for manual sorting
    
    # Calculate graduation rates for each institution
    for institution in institutions:
        # Initialize graduation rates
        institution.completion_rate = None
        
        # First try regular graduation cohorts
        four_year_cohorts = [c for c in institution.graduation_cohorts if c.grtype_code in [2, 3]]
        two_year_cohorts = [c for c in institution.graduation_cohorts if c.grtype_code in [29, 30]]
        
        if four_year_cohorts:
            adjusted_cohort = next((c for c in four_year_cohorts if c.grtype_code == 2), None)
            completers = next((c for c in four_year_cohorts if c.grtype_code == 3), None)
            
            if adjusted_cohort and completers and adjusted_cohort.statuses and completers.statuses:
                total = adjusted_cohort.statuses[0].student_count
                completed = completers.statuses[0].student_count
                if total > 0:
                    institution.completion_rate = (completed / total) * 100
                    
        elif two_year_cohorts:
            adjusted_cohort = next((c for c in two_year_cohorts if c.grtype_code == 29), None)
            completers = next((c for c in two_year_cohorts if c.grtype_code == 30), None)
            
            if adjusted_cohort and completers and adjusted_cohort.statuses and completers.statuses:
                total = adjusted_cohort.statuses[0].student_count
                completed = completers.statuses[0].student_count
                if total > 0:
                    institution.completion_rate = (completed / total) * 100
        
        # If no completion rate found, try IPEDS metrics
        if institution.completion_rate is None and hasattr(institution, 'ipeds_graduation_metrics'):
            ipeds = institution.ipeds_graduation_metrics
            if ipeds and ipeds[0].bachelors_grad_rate_150 is not None:
                institution.completion_rate = ipeds[0].bachelors_grad_rate_150
            elif ipeds and ipeds[0].certificate_grad_rate_150 is not None:
                institution.completion_rate = ipeds[0].certificate_grad_rate_150
    
    # Sort by completion rate if selected
    if sort_by == 'completion_rate':
        institutions.sort(
            key=lambda x: (x.completion_rate is None, x.completion_rate or 0),
            reverse=(direction == 'desc')
        )
    
    # Determine sort icon
    sort_icon = 'down' if direction == 'desc' else 'up'
    
    return render_template('colleges.html', 
                         institutions=institutions,
                         sort_by=sort_by,
                         sort_direction=sort_direction,
                         sort_icon=sort_icon)

@app.route('/institutions/add', methods=['GET', 'POST'])
def add_institution():
    if request.method == 'POST':
        try:
            # Get institution_id from form or use '0' as default
            institution_id = request.form.get('institution_id', '0')
            if not institution_id.strip():  # If empty string
                institution_id = '0'

            # Create new institution from form data
            new_institution = Institution(
                institution_id=institution_id,
                name=request.form['name'],
                alias=request.form['alias'],
                address=request.form['address'],
                city=request.form['city'],
                state=request.form['state'],
                zip=request.form['zip'],
                web_url=request.form['web_url'],
                county=request.form['county'],
                longitude=float(request.form['longitude']),
                latitude=float(request.form['latitude'])
            )
            
            # Add to database
            db.session.add(new_institution)
            db.session.commit()
            
            flash('Institution added successfully!', 'success')
            return redirect(url_for('colleges'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding institution: {str(e)}")
            flash(f'Error adding institution: {str(e)}', 'error')
            return render_template('institutions/add_institution.html', 
                form_data={
                    'institution_id': request.form.get('institution_id', '0'),
                    'name': request.form['name'],
                    'alias': request.form['alias'],
                    'address': request.form['address'],
                    'city': request.form['city'],
                    'state': request.form['state'],
                    'zip': request.form['zip'],
                    'web_url': request.form['web_url'],
                    'county': request.form['county'],
                    'longitude': request.form['longitude'],
                    'latitude': request.form['latitude']
                })
    
    # GET request - show the form
    return render_template('institutions/add_institution.html')

@app.route('/institutions/delete/<int:id>')
def delete_institution(id):
    institution = Institution.query.get(id)
    db.session.delete(institution)
    db.session.commit()
    return redirect(url_for('colleges'))

@app.route('/institutions/edit/<int:id>', methods=['GET', 'POST'])
def edit_institution(id):
    institution = Institution.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Update institution with form data
            institution.name = request.form['name']
            institution.alias = request.form['alias']
            institution.address = request.form['address']
            institution.city = request.form['city']
            institution.state = request.form['state']
            institution.zip = request.form['zip']
            institution.web_url = request.form['web_url']
            institution.county = request.form['county']
            institution.longitude = float(request.form['longitude'])
            institution.latitude = float(request.form['latitude'])
            institution.title_iv_eligible = 'title_iv_eligible' in request.form
            
            # Commit changes to database
            db.session.commit()
            
            flash('Institution updated successfully!', 'success')
            return redirect(url_for('colleges'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating institution. Please try again.', 'error')
            return render_template('institutions/edit_institution.html', institution=institution)
    
    return render_template('institutions/edit_institution.html', institution=institution)

@app.route('/institutions/import', methods=['GET', 'POST'])
def import_institutions():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
            
        file = request.files['file']
        import_type = request.form.get('import_type')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})

        if file and file.filename.endswith('.csv'):
            try:
                # Save the uploaded file temporarily
                temp_path = 'temp_upload.csv'
                file.save(temp_path)
                
                # Read the CSV file
                df = pd.read_csv(temp_path, encoding_errors='replace')
                
                # Delete the temporary file
                os.remove(temp_path)

                # Process based on import type
                if import_type == 'c2023_a':
                    # Only extract year for completion data
                    year_match = re.search(r'\d{4}', file.filename)
                    if not year_match:
                        return jsonify({'success': False, 'error': 'Could not extract year from filename'})
                    year = int(year_match.group())
                    result = import_c2023_a_data(df, year)
                elif import_type == 'gr200':
                    result = import_gr200_data(df)
                elif import_type == 'hd2023':
                    result = import_hd2023_data(df)
                elif import_type == 'ic2023':
                    result = import_ic2023_data(df)
                elif import_type == 'gr2022':
                    result = import_gr2022_data(df)
                else:
                    return jsonify({'success': False, 'error': 'Invalid import type'})

                return jsonify(result)
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Error processing file: {str(e)}'
                })
    
    # GET request - show the upload form
    return render_template('institutions/import_institutions.html')

# General clean_enum_value function for numeric enums
def clean_enum_value(value, enum_class):
    try:
        if pd.isna(value) or value == '' or value == ' ' or value == '-2':
            return enum_class.UNKNOWN
        value = int(float(value))
        return enum_class(value) if value in [e.value for e in enum_class] else enum_class.UNKNOWN
    except (ValueError, TypeError):
        return enum_class.UNKNOWN

def import_hd2023_data(df):
    try:
        # Map the columns to our model fields
        column_mapping = {
            'UNITID': 'institution_id',
            'INSTNM': 'name',
            'IALIAS': 'alias',
            'ADDR': 'address',
            'CITY': 'city',
            'STABBR': 'state',
            'ZIP': 'zip',
            'WEBADDR': 'web_url',
            'COUNTYNM': 'county',
            'LONGITUD': 'longitude',
            'LATITUDE': 'latitude',
            'OPEFLAG': 'title_iv_eligible',
            'ADMINURL': 'admin_url',
            'FAIDURL': 'financial_aid_url',
            'APPLURL': 'application_url',
            'NPRICURL': 'net_price_calculator_url',
            'ATHURL': 'right_to_know_url',
            'DISAURL': 'disability_services_url',
            'ICLEVEL': 'level',
            'CONTROL': 'control',
            'HLOFFER': 'highest_degree',
            'UGOFFER': 'undergraduate_degree_offered',
            'GROFFER': 'graduate_degree_offered',
            'HBCU': 'hbcu',
            'MEDICAL': 'medical_school',
            'LOCALE': 'locale',
            'OPENPUBL': 'open_to_public',
            'ACT': 'status',
            'PSET4FLG': 'pset4_flag',
            'INSTCAT': 'institution_category',
            'INSTSIZE': 'size_classification',
            'C21BASIC': 'carnegie_classification'
        }
        
        # Rename columns according to our mapping
        df = df[column_mapping.keys()]
        df = df.rename(columns=column_mapping)
        
        # Convert empty strings to None for nullable fields
        nullable_fields = ['alias', 'address', 'zip', 'web_url']
        for field in nullable_fields:
            df[field] = df[field].replace('', None)
        
        # Convert OPEFLAG to boolean based on values
        df['title_iv_eligible'] = df['title_iv_eligible'].apply(lambda x: x in [1, 2])
        
        # Convert level and control to appropriate enum values
        def map_level(value):
            try:
                if pd.isna(value):
                    return None
                value = int(value)
                return InstitutionLevel(value if value in [-3, 1, 2, 3] else -3)
            except (ValueError, TypeError):
                return InstitutionLevel.UNKNOWN

        def map_control(value):
            try:
                if pd.isna(value):
                    return None
                value = int(value)
                return InstitutionControl(value if value in [-3, 1, 2, 3] else -3)
            except (ValueError, TypeError):
                return InstitutionControl.UNKNOWN

        df['level'] = df['level'].apply(map_level)
        df['control'] = df['control'].apply(map_control)
        
        def map_highest_degree(value):
            try:
                if pd.isna(value):
                    return None
                value = int(value)
                if value in range(0, 10) or value in [-2, -3] or value == 'b':
                    return HighestDegree(value)
                return HighestDegree(-3)
            except (ValueError, TypeError):
                return HighestDegree(-3)

        def map_degree_offered(value):
            try:
                value = int(value)
                if value == 1:
                    return True
                elif value == 2:
                    return False
                else:
                    return None  # For -3 or any other values, set as unknown
            except (ValueError, TypeError):
                return None

        df['highest_degree'] = df['highest_degree'].apply(map_highest_degree)
        df['undergraduate_degree_offered'] = df['undergraduate_degree_offered'].apply(map_degree_offered)
        df['graduate_degree_offered'] = df['graduate_degree_offered'].apply(map_degree_offered)
        
        # Convert boolean fields (1=True, 2=False, -3=None)
        def map_boolean(value):
            try:
                value = int(value)
                if value == 1:
                    return True
                elif value == 2:
                    return False
                else:
                    return None
            except (ValueError, TypeError):
                return None

        # Add boolean field mappings
        boolean_fields = ['hbcu', 'medical_school', 'open_to_public']
        for field in boolean_fields:
            df[field] = df[field].apply(map_boolean)

        # Map enum fields
        def map_locale(value):
            try:
                if pd.isna(value) or value == '' or value == ' ' or value == '-2':
                    return InstitutionLocale.UNKNOWN
                value = int(float(value))
                valid_values = [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43]
                return InstitutionLocale(value) if value in valid_values else InstitutionLocale.UNKNOWN
            except (ValueError, TypeError):
                return InstitutionLocale.UNKNOWN

        def map_status(value):
            try:
                if pd.isna(value) or value == '' or value == ' ':
                    return None  # Using None since it's nullable
                return InstitutionStatus(value) if value in ['A', 'N', 'M', 'R'] else None
            except (ValueError, TypeError):
                return None

        def map_pset4flag(value):
            try:
                if pd.isna(value) or value == '' or value == ' ' or value == '-2':
                    return Pset4Flag.UNKNOWN
                value = int(float(value))
                return Pset4Flag(value) if value in [0, 1, 2, 3, 4, 5, 9] else Pset4Flag.UNKNOWN
            except (ValueError, TypeError):
                return Pset4Flag.UNKNOWN

        def map_institution_category(value):
            try:
                if pd.isna(value) or value == '':
                    return None
                value = int(float(value))  # Convert to float first in case it's a decimal
                if value in range(1, 7):  # Valid values are 1-6
                    return InstitutionCategory(value)
                return None
            except (ValueError, TypeError):
                return None

        def map_size_classification(value):
            try:
                if pd.isna(value) or value == '':
                    return None
                value = int(float(value))
                valid_values = [11, 12, 13, 14, 15, 21, 22, 23, 31, 32, 33, 41, 42, 43, 51, 52, 53, 60]
                return InstitutionSizeClassification(value) if value in valid_values else None
            except (ValueError, TypeError):
                return None

        def map_carnegie_classification(value):
            try:
                if pd.isna(value) or value == '':
                    return None
                value = int(float(value))
                return CarnegieClassification(value) if value in range(1, 34) else None
            except (ValueError, TypeError):
                return None

        # Apply enum mappings
        df['locale'] = df['locale'].apply(map_locale)
        df['status'] = df['status'].apply(map_status)
        df['pset4_flag'] = df['pset4_flag'].apply(map_pset4flag)
        df['institution_category'] = df['institution_category'].apply(map_institution_category)
        df['size_classification'] = df['size_classification'].apply(map_size_classification)
        df['carnegie_classification'] = df['carnegie_classification'].apply(map_carnegie_classification)
        
        # Create Institution objects and add to database
        success_count = 0
        error_count = 0

        for _, row in df.iterrows():
            try:
                institution = Institution(
                    institution_id=str(row['institution_id']),
                    name=row['name'],
                    alias=row['alias'],
                    address=row['address'],
                    city=row['city'],
                    state=row['state'],
                    zip=row['zip'],
                    web_url=row['web_url'],
                    county=row['county'],
                    longitude=float(row['longitude']),
                    latitude=float(row['latitude']),
                    title_iv_eligible=row['title_iv_eligible'],
                    admin_url=row['admin_url'],
                    financial_aid_url=row['financial_aid_url'],
                    application_url=row['application_url'],
                    net_price_calculator_url=row['net_price_calculator_url'],
                    right_to_know_url=row['right_to_know_url'],
                    disability_services_url=row['disability_services_url'],
                    level=clean_enum_value(row['level'], InstitutionLevel),
                    control=clean_enum_value(row['control'], InstitutionControl),
                    highest_degree=clean_enum_value(row['highest_degree'], HighestDegree),
                    undergraduate_degree_offered=row['undergraduate_degree_offered'],
                    graduate_degree_offered=row['graduate_degree_offered'],
                    hbcu=row['hbcu'],
                    medical_school=row['medical_school'],
                    locale=clean_enum_value(row['locale'], InstitutionLocale),
                    open_to_public=row['open_to_public'],
                    status=map_status(row['status']),
                    pset4_flag=clean_enum_value(row['pset4_flag'], Pset4Flag),
                    institution_category=clean_enum_value(row['institution_category'], InstitutionCategory),
                    size_classification=clean_enum_value(row['size_classification'], InstitutionSizeClassification),
                    carnegie_classification=clean_enum_value(row['carnegie_classification'], CarnegieClassification)
                )
                db.session.add(institution)
                success_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error processing row: {str(e)}")
        
        # Commit all successful additions
        db.session.commit()
        
        message = f'Successfully imported {success_count} institutions.'
        if error_count > 0:
            message += f' {error_count} records had errors and were skipped.'
        
        return {
            'success': True,
            'message': message
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Error importing data: {str(e)}'
        }

def clean_standardized_answer(value):
    """Convert numeric values to StandardizedAnswer enum
    1 = YES
    2 = NO
    -2 = UNKNOWN
    """
    try:
        if pd.isna(value) or value == '' or value == ' ':
            return StandardizedAnswer.UNKNOWN
        value = int(float(value))
        if value == 1:
            return StandardizedAnswer.YES
        elif value == 2:
            return StandardizedAnswer.NO
        else:
            return StandardizedAnswer.UNKNOWN
    except (ValueError, TypeError):
        return StandardizedAnswer.UNKNOWN

def import_ic2023_data(df):
    try:
        # Rest of your column mapping
        column_mapping = {
            'UNITID': 'institution_id',
            'CREDITS3': 'advance_placement_credits_accepted',
            'CREDITS4': 'credit_for_any_credits',
            'SLO5': 'rotc_offered',
            'SLO51': 'rotc_army_offered',
            'SLO52': 'rotc_navy_offered',
            'SLO53': 'rotc_airforce_offered',
            'SLO521': 'rotc_marine_offered',
            'SLO6': 'study_abroad_offered',
            'SLO7': 'weekend_college_offered',
            'SLO81': 'specialized_teacher_preparation_offered',
            'SLO8': 'teacher_certification_offered',
            'SLO83': 'no_teacher_certification_offered',
            'SLOA': 'undergraduate_teacher_offered',
            'SLOB': 'transition_program_for_disabled_students_offered',
            'STUSRV2': 'academic_counseling_offered',
            'STUSRV3': 'employment_services_offered',
            'STUSRV4': 'placement_services_offered',
            'STUSRV8': 'oncampus_daycare_offered',
            'STUSRV9': 'no_student_services_offered',
            'LIBRES1': 'physical_library_offered',
            'LIBRES2': 'printed_materials_library_offered',
            'LIBRES3': 'online_library_offered',
            'LIBRES4': 'trained_librarian_available',
            'LIBRES5': 'no_library_services_offered',
            'TUITPL1': 'alternative_tuition_offered',
            'TUITPL2': 'tuition_guaranteed_plan_offered',
            'TUITPL3': 'tuition_payment_plan_offered',
            'TUITPL4': 'other_alternative_tuition_offered',
            'ALLONCAM': 'required_live_on_campus',
            'ROOM': 'oncampus_housing_offered',
            
            'DISABPCT': 'disabled_students_percentage',
            'ROOMCAP': 'oncampus_capacity',
            
            'BOARD': 'meal_plan_offered',
            'MEALSWK': 'number_of_meals_per_week',
            'ROOMAMT': 'housing_charge_per_year',
            'BOARDAMT': 'meal_plan_charge_per_year',
            'RMBRDAMT': 'combined_charge_per_year',
            'APPLFEEU': 'undergraduate_application_fee',
            'APPLFEEG': 'graduate_application_fee',
            
            'ATHASSOC': 'member_of_naa',
            'ASSOC1': 'member_of_ncaa',
            'ASSOC2': 'member_of_naia',
            'ASSOC3': 'member_of_njcaa',
            'ASSOC4': 'member_of_nscaa',
            'ASSOC5': 'member_of_nccaa',
            'ASSOC6': 'member_of_other_athletic_association',
            'SPORT1': 'member_of_ncaaa_football'
        }

        # Convert UNITID to string right after reading
        df['UNITID'] = df['UNITID'].astype(int).astype(str)
        
        def clean_numeric(value):
            """Clean numeric values from the CSV data"""
            if pd.isna(value) or (isinstance(value, str) and value.strip() in ['.', '. ', '-2']):
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        # Define numeric columns with their original CSV column names
        integer_columns = {
            'ROOMCAP': 'oncampus_capacity',
            'MEALSWK': 'number_of_meals_per_week',
            'ROOMAMT': 'housing_charge_per_year',
            'BOARDAMT': 'meal_plan_charge_per_year',
            'RMBRDAMT': 'combined_charge_per_year',
            'APPLFEEU': 'undergraduate_application_fee',
            'APPLFEEG': 'graduate_application_fee'
        }
        
        float_columns = {
            'DISABPCT': 'disabled_students_percentage'
        }
        
        # Clean numeric columns using original column names
        for original_col, new_col in integer_columns.items():
            df[original_col] = df[original_col].map(lambda x: None if pd.isna(x) else 
                                                  int(float(x)) if isinstance(x, (int, float, str)) and str(x).strip() not in ['', '.', '. ', '-2'] 
                                                  else None)
            
        for original_col, new_col in float_columns.items():
            df[original_col] = df[original_col].map(lambda x: None if pd.isna(x) else 
                                                  float(x) if isinstance(x, (int, float, str)) and str(x).strip() not in ['', '.', '. ', '-2'] 
                                                  else None)

        # Convert numeric values to StandardizedAnswer enum
        for column in [col for col in df.columns if col.endswith('_offered') or col.endswith('_available')]:
            df[column] = df[column].apply(clean_standardized_answer)
        
        # Rename columns after cleaning
        df = df[column_mapping.keys()]
        df = df.rename(columns=column_mapping)

        success_count = 0
        error_count = 0

        for _, row in df.iterrows():
            try:
                institution = Institution.query.filter_by(institution_id=str(row['institution_id'])).first()
                if not institution:
                    error_count += 1
                    print(f"Institution not found: {row['institution_id']}")
                    continue

                try:
                    attributes = Institutional_Attributes(
                        institution_id=str(row['institution_id']),
                        advance_placement_credits_accepted=clean_enum_value(row['advance_placement_credits_accepted'], StandardizedAnswer),
                        credit_for_any_credits=clean_enum_value(row['credit_for_any_credits'], StandardizedAnswer),
                        rotc_offered=clean_enum_value(row['rotc_offered'], StandardizedAnswer),
                        rotc_army_offered=clean_enum_value(row['rotc_army_offered'], StandardizedAnswer),
                        rotc_navy_offered=clean_enum_value(row['rotc_navy_offered'], StandardizedAnswer),
                        rotc_airforce_offered=clean_enum_value(row['rotc_airforce_offered'], StandardizedAnswer),
                        rotc_marine_offered=clean_enum_value(row['rotc_marine_offered'], StandardizedAnswer),
                        study_abroad_offered=clean_enum_value(row['study_abroad_offered'], StandardizedAnswer),
                        weekend_college_offered=clean_enum_value(row['weekend_college_offered'], StandardizedAnswer),
                        specialized_teacher_preparation_offered=clean_enum_value(row['specialized_teacher_preparation_offered'], StandardizedAnswer),
                        teacher_certification_offered=clean_enum_value(row['teacher_certification_offered'], StandardizedAnswer),
                        no_teacher_certification_offered=clean_enum_value(row['no_teacher_certification_offered'], StandardizedAnswer),
                        undergraduate_teacher_offered=clean_enum_value(row['undergraduate_teacher_offered'], StandardizedAnswer),
                        transition_program_for_disabled_students_offered=clean_enum_value(row['transition_program_for_disabled_students_offered'], StandardizedAnswer),
                        academic_counseling_offered=clean_enum_value(row['academic_counseling_offered'], StandardizedAnswer),
                        employment_services_offered=clean_enum_value(row['employment_services_offered'], StandardizedAnswer),
                        placement_services_offered=clean_enum_value(row['placement_services_offered'], StandardizedAnswer),
                        oncampus_daycare_offered=clean_enum_value(row['oncampus_daycare_offered'], StandardizedAnswer),
                        no_student_services_offered=clean_enum_value(row['no_student_services_offered'], StandardizedAnswer),
                        physical_library_offered=clean_enum_value(row['physical_library_offered'], StandardizedAnswer),
                        printed_materials_library_offered=clean_enum_value(row['printed_materials_library_offered'], StandardizedAnswer),
                        online_library_offered=clean_enum_value(row['online_library_offered'], StandardizedAnswer),
                        trained_librarian_available=clean_enum_value(row['trained_librarian_available'], StandardizedAnswer),
                        no_library_services_offered=clean_enum_value(row['no_library_services_offered'], StandardizedAnswer),
                        alternative_tuition_offered=clean_enum_value(row['alternative_tuition_offered'], StandardizedAnswer),
                        tuition_guaranteed_plan_offered=clean_enum_value(row['tuition_guaranteed_plan_offered'], StandardizedAnswer),
                        tuition_payment_plan_offered=clean_enum_value(row['tuition_payment_plan_offered'], StandardizedAnswer),
                        other_alternative_tuition_offered=clean_enum_value(row['other_alternative_tuition_offered'], StandardizedAnswer),
                        required_live_on_campus=clean_enum_value(row['required_live_on_campus'], StandardizedAnswer),
                        oncampus_housing_offered=clean_enum_value(row['oncampus_housing_offered'], StandardizedAnswer),
                        
                        disabled_students_percentage=row['disabled_students_percentage'],
                        oncampus_capacity=row['oncampus_capacity'],
                        number_of_meals_per_week=row['number_of_meals_per_week'],
                        housing_charge_per_year=row['housing_charge_per_year'],
                        meal_plan_charge_per_year=row['meal_plan_charge_per_year'],
                        combined_charge_per_year=row['combined_charge_per_year'],
                        undergraduate_application_fee=row['undergraduate_application_fee'],
                        graduate_application_fee=row['graduate_application_fee'],
                        
                        member_of_naa=clean_enum_value(row['member_of_naa'], StandardizedAnswer),
                        member_of_ncaa=clean_enum_value(row['member_of_ncaa'], StandardizedAnswer),
                        member_of_naia=clean_enum_value(row['member_of_naia'], StandardizedAnswer),
                        member_of_njcaa=clean_enum_value(row['member_of_njcaa'], StandardizedAnswer),
                        member_of_nscaa=clean_enum_value(row['member_of_nscaa'], StandardizedAnswer),
                        member_of_nccaa=clean_enum_value(row['member_of_nccaa'], StandardizedAnswer),
                        member_of_other_athletic_association=clean_enum_value(row['member_of_other_athletic_association'], StandardizedAnswer),
                        member_of_ncaaa_football=clean_enum_value(row['member_of_ncaaa_football'], StandardizedAnswer)
                    )
                    db.session.add(attributes)
                    success_count += 1
                except Exception as attr_error:
                    error_count += 1
                    print(f"Error creating attributes for institution {row['institution_id']}")
                    print(f"Full error details: {str(attr_error)}")
                    print(f"Error type: {type(attr_error)}")
                    
                    # Print all values for debugging
                    print("All attribute values:")
                    for key, value in row.items():
                        print(f"  {key}: {value} (type: {type(value)})")
                
            except Exception as row_error:
                error_count += 1
                print(f"Row level error for institution {row['institution_id']}: {str(row_error)}")
                
        try:
            db.session.commit()
            print(f"Final commit completed. Success: {success_count}, Errors: {error_count}")
        except Exception as commit_error:
            print(f"Error during final commit: {str(commit_error)}")
            db.session.rollback()
            
        return {
            'success': True if success_count > 0 else False,
            'message': f'Imported {success_count} records. {error_count} errors.'
        }
        
    except Exception as e:
        print(f"Top level error: {str(e)}")
        print(f"Error type: {type(e)}")
        db.session.rollback()
        return {
            'success': False,
            'error': f'Error importing data: {str(e)}'
        }

@app.route('/institutions/view/<int:id>')
def view_institution(id):
    institution = Institution.query.get_or_404(id)
    return render_template('institutions/view_institution.html', institution=institution)

@app.route('/institutions/<int:id>/attributes')
def view_institution_attributes(id):
    institution = Institution.query.options(
        db.joinedload(Institution.institutional_attributes)
    ).get_or_404(id)
    
    # Get the first (and should be only) attributes record
    attributes = institution.institutional_attributes[0] if institution.institutional_attributes else None
    
    if not attributes:
        flash('No attributes data available for this institution.', 'error')
        return redirect(url_for('view_institution', id=id))
        
    return render_template('institutions/attributes.html', 
                         institution=institution,
                         attributes=attributes)

def import_c2023_a_data(df, year):
    try:
        # Map the columns to our model fields
        column_mapping = {
            'UNITID': 'institution_id',
            'CIPCODE': 'program_classification_code',
            'MAJORNUM': 'first_major',
            'AWLEVEL': 'award_level_code',
            'CTOTALT': 'total_completions'
        }

        # Rename columns according to our mapping
        df = df[column_mapping.keys()]
        df = df.rename(columns=column_mapping)
        
        # Convert UNITID to string
        df['institution_id'] = df['institution_id'].astype(str)
        
        # Clean and convert award level codes
        def map_award_level(value):
            try:
                value = int(float(value))
                return AwardLevel(value) if value in [2, 3, 4, 5, 6, 7, 8, 17, 18, 19, 20, 21] else None
            except (ValueError, TypeError):
                return None

        # Convert 'R' values to None for total_completions
        def clean_completions(x):
            if pd.isna(x) or x == 'R':
                return None
            try:
                return float(x)
            except (ValueError, TypeError):
                return None

        df['total_completions'] = df['total_completions'].apply(clean_completions)

        success_count = 0
        error_count = 0

        # Clean classification codes to match dictionary format
        def clean_classification_code(code):
            try:
                # Convert to string and remove trailing zeros after decimal
                return str(float(code)).rstrip('0').rstrip('.')
            except (ValueError, TypeError):
                return str(code)

        for _, row in df.iterrows():
            try:
                # Find the institution
                institution = Institution.query.filter_by(institution_id=str(row['institution_id'])).first()
                if not institution:
                    error_count += 1
                    print(f"Institution not found: {row['institution_id']}")
                    continue

                # Clean and get program classification
                clean_code = clean_classification_code(row['program_classification_code'])
                program_classification = CLASSIFICATION_CODES.get(clean_code)
                
                if not program_classification:
                    error_count += 1
                    print(f"Classification code not found: {clean_code} (original: {row['program_classification_code']})")
                    continue

                # Create completion record
                completion = Completitions(
                    institution_id=str(row['institution_id']),
                    program_classification_code=clean_code,
                    program_classification=program_classification,
                    first_major=row['first_major'],
                    award_level_code=map_award_level(row['award_level_code']),
                    total_completions=row['total_completions'],
                    year=year
                )
                
                db.session.add(completion)
                success_count += 1
                
                # Report progress every 10000 successful imports
                if success_count % 10000 == 0:
                    print(f"Successfully processed {success_count} records...")
                
            except Exception as e:
                error_count += 1
                print(f"Error processing row: {str(e)}")
                print(f"Row data: {row}")
                continue

        db.session.commit()
        
        return {
            'success': True,
            'message': f'Successfully imported {success_count} completion records. {error_count} errors.'
        }
        
    except Exception as e:
        db.session.rollback()
        print(f"Top level error: {str(e)}")
        return {
            'success': False,
            'error': f'Error importing completion data: {str(e)}'
        }

@app.route('/institutions/<int:id>/completions')
def view_institution_completions(id):
    institution = Institution.query.options(
        db.joinedload(Institution.completitions)
    ).get_or_404(id)
    
    # Get sort parameters
    sort_by = request.args.get('sort', 'program_classification')
    direction = request.args.get('direction', 'asc')
    search = request.args.get('search', '').strip().lower()
    award_filter = request.args.get('award_level', '') 
    
    # Filter completions for first_major = 1
    completions = [c for c in institution.completitions if int(float(c.first_major)) == 1]
    
    # Apply search if provided
    if search:
        completions = [c for c in completions 
                      if search in c.program_classification.lower()]
    
    # Apply award level filter if provided
    if award_filter:
        try:
            award_filter = int(award_filter)
            completions = [c for c in completions 
                         if c.award_level_code and c.award_level_code.value == award_filter]
        except ValueError:
            pass  # Invalid award filter value, ignore it
    
    # Group completions by degree type
    certificates_completions = sum(c.total_completions or 0 for c in completions 
                                if c.award_level_code in [
                                    AwardLevel.CERTIFICATE_UNDER_1_YEAR,
                                    AwardLevel.CERTIFICATE_1_YEAR,
                                    AwardLevel.CERTIFICATE_2_YEAR,
                                    AwardLevel.CERTIFICATE_4_YEAR
                                ])
    
    associates_completions = sum(c.total_completions or 0 for c in completions 
                               if c.award_level_code == AwardLevel.ASSOCIATES)
    
    bachelors_completions = sum(c.total_completions or 0 for c in completions 
                              if c.award_level_code == AwardLevel.BACHELORS)
    
    masters_completions = sum(c.total_completions or 0 for c in completions 
                            if c.award_level_code == AwardLevel.MASTERS)
    
    post_certificates_completions = sum(c.total_completions or 0 for c in completions 
                                      if c.award_level_code in [
                                          AwardLevel.POST_BACCALAUREATE,
                                          AwardLevel.POST_MASTERS
                                      ])
    
    doctorate_completions = sum(c.total_completions or 0 for c in completions 
                              if c.award_level_code in [
                                  AwardLevel.DOCTORATE_RESEARCH,
                                  AwardLevel.DOCTORATE_PROFESSIONAL,
                                  AwardLevel.DOCTORATE_OTHER
                              ])
    
    # Apply sorting
    reverse = direction == 'desc'
    if sort_by == 'program_classification':
        completions.sort(key=lambda x: x.program_classification, reverse=reverse)
    elif sort_by == 'classification_code':
        completions.sort(key=lambda x: x.program_classification_code, reverse=reverse)
    elif sort_by == 'award_level':
        completions.sort(key=lambda x: x.award_level_code.value if x.award_level_code else -1, reverse=reverse)
    elif sort_by == 'total_completions':
        completions.sort(key=lambda x: x.total_completions if x.total_completions else 0, reverse=reverse)
    
    if not completions:
        flash('No completions data available for this institution.', 'info')
        
    return render_template('institutions/view_completion_data.html', 
                         institution=institution,
                         completions=completions,
                         sort_by=sort_by,
                         sort_direction=direction,
                         certificates_completions=certificates_completions,
                         associates_completions=associates_completions,
                         bachelors_completions=bachelors_completions,
                         masters_completions=masters_completions,
                         post_certificates_completions=post_certificates_completions,
                         doctorate_completions=doctorate_completions)

@app.route('/degrees')
def view_degrees():
    # Get filter parameters
    search = request.args.get('search', '').strip().lower()
    state_filter = request.args.get('state', '')
    award_filter = request.args.get('award_level', '')
    year_filter = request.args.get('year', '2023')  # Default to 2023
    sort_by = request.args.get('sort', 'program_classification')
    direction = request.args.get('direction', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Start with base query
    query = Completitions.query.join(Institution).filter(
        Institution.state.in_(['KS', 'MO']),
        Completitions.first_major == '1',
        Completitions.year == int(year_filter)  # Add year filter
    )
    
    # Apply filters
    if search:
        query = query.filter(Completitions.program_classification.ilike(f'%{search}%'))
    if state_filter:
        query = query.filter(Institution.state == state_filter)
    if award_filter:
        try:
            award_enum = AwardLevel(int(award_filter))
            query = query.filter(Completitions.award_level_code == award_enum)
        except (ValueError, TypeError):
            pass  # Invalid award filter value, ignore it
    
    # Apply sorting
    if sort_by == 'program_classification':
        query = query.order_by(
            Completitions.program_classification.desc() if direction == 'desc' 
            else Completitions.program_classification
        )
    elif sort_by == 'award_level':
        query = query.order_by(
            Completitions.award_level_code.desc() if direction == 'desc' 
            else Completitions.award_level_code
        )
    elif sort_by == 'total_completions':
        query = query.order_by(
            Completitions.total_completions.desc() if direction == 'desc' 
            else Completitions.total_completions
        )
    
    # Get paginated results
    completions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Calculate completion totals
    all_completions = query.all()
    certificates_completions = sum(c.total_completions or 0 for c in all_completions 
                                if c.award_level_code in [
                                    AwardLevel.CERTIFICATE_UNDER_1_YEAR,
                                    AwardLevel.CERTIFICATE_1_YEAR,
                                    AwardLevel.CERTIFICATE_2_YEAR
                                ])
    associates_completions = sum(c.total_completions or 0 for c in all_completions 
                               if c.award_level_code == AwardLevel.ASSOCIATES)
    bachelors_completions = sum(c.total_completions or 0 for c in all_completions 
                              if c.award_level_code == AwardLevel.BACHELORS)
    masters_completions = sum(c.total_completions or 0 for c in all_completions 
                            if c.award_level_code == AwardLevel.MASTERS)
    doctorate_completions = sum(c.total_completions or 0 for c in all_completions 
                              if c.award_level_code in [
                                  AwardLevel.DOCTORATE_RESEARCH,
                                  AwardLevel.DOCTORATE_PROFESSIONAL,
                                  AwardLevel.DOCTORATE_OTHER
                              ])
    
    return render_template('degrees/degrees.html',
                         completions=completions,
                         certificates_completions=certificates_completions,
                         associates_completions=associates_completions,
                         bachelors_completions=bachelors_completions,
                         masters_completions=masters_completions,
                         doctorate_completions=doctorate_completions,
                         sort_by=sort_by,
                         sort_direction=direction,
                         page=page)

@app.route('/degrees/summary')
def view_degrees_summary():
    # Get filter parameters
    search = request.args.get('search', '').strip().lower()
    state_filter = request.args.get('state', '')
    award_filter = request.args.get('award_level', '')
    year_filter = request.args.get('year', '2023')  # Default to 2023
    sort_by = request.args.get('sort', 'program_classification')
    direction = request.args.get('direction', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Start with base query for filtered totals
    filtered_query = Completitions.query.join(Institution).filter(
        Institution.state.in_(['KS', 'MO']),
        Completitions.first_major == '1',
        Completitions.year == int(year_filter)  # Add year filter
    )
    
    # Apply filters to the totals query
    if search:
        filtered_query = filtered_query.filter(Completitions.program_classification.ilike(f'%{search}%'))
    if state_filter:
        filtered_query = filtered_query.filter(Institution.state == state_filter)
    
    # Get filtered completions for totals
    filtered_completions = filtered_query.all()
    
    # Calculate completion totals using filtered results
    certificates_completions = sum(c.total_completions or 0 for c in filtered_completions 
                                if c.award_level_code in [
                                    AwardLevel.CERTIFICATE_UNDER_1_YEAR,
                                    AwardLevel.CERTIFICATE_1_YEAR,
                                    AwardLevel.CERTIFICATE_2_YEAR,
                                    AwardLevel.CERTIFICATE_4_YEAR
                                ])
    associates_completions = sum(c.total_completions or 0 for c in filtered_completions 
                               if c.award_level_code == AwardLevel.ASSOCIATES)
    bachelors_completions = sum(c.total_completions or 0 for c in filtered_completions 
                              if c.award_level_code == AwardLevel.BACHELORS)
    masters_completions = sum(c.total_completions or 0 for c in filtered_completions 
                            if c.award_level_code == AwardLevel.MASTERS)
    doctorate_completions = sum(c.total_completions or 0 for c in filtered_completions 
                              if c.award_level_code in [
                                  AwardLevel.DOCTORATE_RESEARCH,
                                  AwardLevel.DOCTORATE_PROFESSIONAL,
                                  AwardLevel.DOCTORATE_OTHER
                              ])
    
    # Query for grouped results
    base_query = db.session.query(
        Completitions.program_classification,
        Completitions.award_level_code,
        db.func.sum(Completitions.total_completions).label('total_completions')
    ).join(Institution).filter(
        Institution.state.in_(['KS', 'MO']),
        Completitions.first_major == '1',
        Completitions.year == int(year_filter)  # Add year filter
    ).group_by(
        Completitions.program_classification,
        Completitions.award_level_code
    )
    
    # Apply same filters to grouped results
    if search:
        base_query = base_query.filter(Completitions.program_classification.ilike(f'%{search}%'))
    if state_filter:
        base_query = base_query.filter(Institution.state == state_filter)
    if award_filter:
        try:
            award_enum = AwardLevel(int(award_filter))
            base_query = base_query.filter(Completitions.award_level_code == award_enum)
        except (ValueError, TypeError):
            pass
    
    # Apply sorting
    if sort_by == 'program_classification':
        base_query = base_query.order_by(
            Completitions.program_classification.desc() if direction == 'desc' 
            else Completitions.program_classification
        )
    elif sort_by == 'award_level':
        base_query = base_query.order_by(
            Completitions.award_level_code.desc() if direction == 'desc' 
            else Completitions.award_level_code
        )
    elif sort_by == 'total_completions':
        base_query = base_query.order_by(
            db.desc('total_completions') if direction == 'desc' 
            else db.asc('total_completions')
        )
    
    # Get paginated results
    programs = base_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('degrees/degrees_summary.html',
                         programs=programs,
                         certificates_completions=certificates_completions,
                         associates_completions=associates_completions,
                         bachelors_completions=bachelors_completions,
                         masters_completions=masters_completions,
                         doctorate_completions=doctorate_completions,
                         sort_by=sort_by,
                         sort_direction=direction,
                         page=page)

def import_gr2022_data(df):
    try:
        # Map the columns to our model fields
        column_mapping = {
            'UNITID': 'institution_id',
            'GRTYPE': 'grtype_code',
            'CHRTSTAT': 'chrtstat_code',
            'SECTION': 'section_code',
            'GRTOTLT': 'student_count'  # Total count of students
        }

        # Create lookup dictionaries for labels based on the provided codes
        grtype_labels = {
            40: "Total exclusions 4-year schools",
            2: "4-year institutions, Adjusted cohort (revised cohort minus exclusions)",
            3: "4-year institutions, Completers within 150% of normal time",
            4: "4-year institutions, Transfer-out students",
            41: "4-year institutions, noncompleters still enrolled",
            42: "4-year institutions, No longer enrolled",
            6: "Bachelor's or equiv subcohort (4-yr institution)",
            7: "Bachelor's or equiv subcohort (4-yr institution) exclusions",
            8: "Bachelor's or equiv subcohort (4-yr institution) adjusted cohort",
            9: "Bachelor's or equiv subcohort (4-yr institution) Completers within 150% of normal time total",
            10: "Bachelor's or equiv subcohort (4-yr institution) Completers of programs of < 2 yrs (150% of normal time)",
            11: "Bachelor's or equiv subcohort (4-yr institution) Completers of programs of 2 but <4 yrs (150% of normal time)",
            12: "Bachelor's or equiv subcohort (4-yr institution) Completers of bachelor's or equiv degrees total (150% of normal time)",
            13: "Bachelor's or equiv subcohort (4-yr institution) Completers of bachelor's or equiv degrees in 4 years or less",
            14: "Bachelor's or equiv subcohort (4-yr institution) Completers of bachelor's or equiv degrees in 5 years",
            15: "Bachelor's or equiv subcohort (4-yr institution) Completers of bachelor's or equiv degrees in 6 years",
            16: "Bachelor's or equiv subcohort (4-yr institution) Transfer-out students",
            43: "Bachelor's or equiv subcohort (4-yr institution) noncompleters still enrolled",
            44: "Bachelor's or equiv subcohort (4-yr institution), No longer enrolled",
            18: "Other degree/certif-seeking subcohort (4-yr institution)",
            19: "Other degree/certificate-seeking subcohort(4-yr institution) exclusions",
            20: "Other degree/certif-seeking subcohort (4-yr institution) Adjusted cohort",
            21: "Other degree/certif-seeking subcohort (4-yr institution) Completers within 150% of normal time total",
            22: "Other degree/certif-seeking subcohort (4-yr institution) Completers of programs < 2 yrs (150% of normal time)",
            23: "Other degree/certif-seeking subcohort (4-yr institution) Completers of programs of 2 but < 4 yrs (150% of normal time)",
            24: "Other degree/certif-seeking subcohort (4-yr institution) Completers of bachelor's or equiv degrees (150% of normal time)",
            25: "Other degree/certif-seeking subcohort (4-yr institution) Transfer-out students",
            45: "Other degree/certif-seeking subcohort (4-yr institution) noncompleters still enrolled",
            46: "Other degree/certif-seeking subcohort (4-yr institution) No longer enrolled",
            28: "Degree/certificate-seeking subcohort(2-yr institution) exclusions",
            29: "Degree/certif-seeking students ( 2-yr institution) Adjusted cohort",
            30: "Degree/certif-seeking students ( 2-yr institution) Completers within 150% of normal time total",
            31: "Degree/certif-seeking students ( 2-yr institution) Completers of programs of < 2 yrs (150% of normal time)",
            32: "Degree/certificate-seeking students ( 2-yr institution) Completers of programs of 2 but < 4 yrs (150% of normal time)",
            35: "Degree/certif-seeking students ( 2-yr institution) Completers within 100% of normal time total",
            36: "Degree/certif-seeking students ( 2-yr institution) Completers of programs of < 2 yrs (100% of normal time)",
            37: "Degree/certif-seeking students ( 2-yr institution) Completers of programs of 2 but < 4 yrs (100% of normal time)",
            33: "Degree/certif-seeking students ( 2-yr institution) Transfer-out students",
            47: "Degree/certif-seeking students ( 2-yr institution) noncompleters still enrolled",
            48: "Degree/certif-seeking students ( 2-yr institution) No longer enrolled"
        }

        chrtstat_labels = {
            40: "Total exclusions 4-year schools",
            2: "4-year institutions, Adjusted cohort",
            3: "4-year institutions, Completers within 150% of normal time",
            4: "4-year institutions, Transfer-out students",
            41: "4-year institutions, noncompleters still enrolled",
            42: "4-year institutions, No longer enrolled",
            6: "Bachelor's or equiv subcohort",
            7: "Bachelor's or equiv subcohort exclusions",
            8: "Bachelor's or equiv subcohort adjusted cohort",
            9: "Completers within 150% of normal time total",
            10: "Completers of programs of < 2 yrs",
            11: "Completers of programs of 2 but <4 yrs",
            12: "Completers of bachelor's or equiv degrees total",
            13: "Completers of bachelor's or equiv degrees in 4 years or less",
            14: "Completers of bachelor's or equiv degrees in 5 years",
            15: "Completers of bachelor's or equiv degrees in 6 years",
            16: "Transfer-out students",
            43: "Noncompleters still enrolled",
            44: "No longer enrolled"
        }

        section_labels = {
            1: "First-time, full-time student cohort",
            2: "Bachelor's or equivalent degree-seeking subcohort"
        }

        success_count = 0
        error_count = 0

        # Group by institution and GRTYPE to create cohorts
        for (inst_id, grtype), group in df.groupby(['UNITID', 'GRTYPE']):
            try:
                # Find the institution
                institution = Institution.query.filter_by(institution_id=str(inst_id)).first()
                if not institution:
                    error_count += 1
                    print(f"Institution not found: {inst_id}")
                    continue

                # Create or update the graduation cohort
                section_code = group['SECTION'].iloc[0] if 'SECTION' in group.columns else None
                
                cohort = GraduationCohort(
                    institution_id=int(inst_id),
                    grtype_code=int(grtype),
                    grtype_label=grtype_labels.get(int(grtype), 'Unknown'),
                    section_code=section_code,
                    section_label=section_labels.get(section_code) if section_code else None
                )
                db.session.add(cohort)
                db.session.flush()  # Get the cohort ID

                # Create graduation statuses for each CHRTSTAT in the group
                for _, row in group.iterrows():
                    if pd.notna(row['CHRTSTAT']):
                        chrtstat_code = int(row['CHRTSTAT'])
                        student_count = row['GRTOTLT']
                        
                        # Skip if student count is 'R' (restricted) or invalid
                        if isinstance(student_count, str) and student_count.strip() == 'R':
                            continue
                            
                        try:
                            student_count = int(float(student_count))
                        except (ValueError, TypeError):
                            continue

                        status = GraduationStatus(
                            cohort_id=cohort.id,
                            chrtstat_code=chrtstat_code,
                            chrtstat_label=chrtstat_labels.get(chrtstat_code, 'Unknown'),
                            student_count=student_count
                        )
                        db.session.add(status)

                success_count += 1

            except Exception as e:
                error_count += 1
                print(f"Error processing institution {inst_id}: {str(e)}")
                db.session.rollback()
                continue

        db.session.commit()
        
        return {
            'success': True,
            'message': f'Successfully imported {success_count} graduation cohorts. {error_count} errors.'
        }
        
    except Exception as e:
        db.session.rollback()
        print(f"Top level error: {str(e)}")
        return {
            'success': False,
            'error': f'Error importing graduation data: {str(e)}'
        }

@app.route('/institutions/<int:id>/graduation_rates')
def view_graduation_rates(id):
    institution = Institution.query.get_or_404(id)
    
    # Get IPEDS metrics
    ipeds_metrics = IPEDSGraduationMetrics.query.filter_by(
        institution_id=institution.id
    ).first()
    
    # Get all cohorts with their statuses
    cohorts = GraduationCohort.query.filter_by(
        institution_id=institution.institution_id
    ).options(
        db.joinedload(GraduationCohort.statuses)
    ).all()

    # Initialize graduation data structure
    graduation_data = {
        'four_year': [],
        'two_year': []  # Add two_year list
    }

    # Filter for relevant cohorts
    four_year_grtypes = [2, 3, 4, 41, 42]  # 4-year institution codes
    two_year_grtypes = [28, 29, 30, 31, 32, 33, 47, 48]  # 2-year institution codes
    
    for cohort in cohorts:
        cohort_data = {
            'cohort': cohort,
            'statuses': cohort.statuses
        }
        
        if cohort.grtype_code in four_year_grtypes:
            graduation_data['four_year'].append(cohort_data)
        elif cohort.grtype_code in two_year_grtypes:
            graduation_data['two_year'].append(cohort_data)

    return render_template(
        'institutions/view_graduation_rates.html',
        institution=institution,
        graduation_data=graduation_data,
        ipeds_metrics=ipeds_metrics
    )

def import_gr200_data(df):
    try:
        success_count = 0
        error_count = 0

        # Process each row in the dataframe
        for _, row in df.iterrows():
            try:
                # Find the institution by UNITID
                institution = Institution.query.filter_by(institution_id=str(row['UNITID'])).first()
                if not institution:
                    error_count += 1
                    print(f"Institution not found: {row['UNITID']}")
                    continue

                # Create or update IPEDS metrics
                metrics = IPEDSGraduationMetrics.query.filter_by(
                    institution_id=institution.id
                ).first() or IPEDSGraduationMetrics(institution_id=institution.id)

                def safe_convert(value, default=None):
                    if pd.isna(value) or value == '' or value == 'R':  # Handle 'R' values
                        return default
                    try:
                        return int(float(value)) if isinstance(value, (str, int, float)) else default
                    except (ValueError, TypeError):
                        return default

                def safe_convert_float(value, default=None):
                    if pd.isna(value) or value == '' or value == 'R':  # Handle 'R' values
                        return default
                    try:
                        return float(value) if isinstance(value, (str, int, float)) else default
                    except (ValueError, TypeError):
                        return default

                # Update all fields from the CSV
                metrics.bachelors_revised_cohort = safe_convert(row.get('BAREVCT'))
                metrics.bachelors_completed_100pct = safe_convert(row.get('BANC100'))
                metrics.bachelors_completed_150pct = safe_convert(row.get('BANC150'))
                metrics.bachelors_completed_200pct = safe_convert(row.get('BANC200'))
                metrics.bachelors_still_enrolled = safe_convert(row.get('BASTEND'))
                
                metrics.bachelors_grad_rate_100 = safe_convert_float(row.get('BAGR100'))
                metrics.bachelors_grad_rate_150 = safe_convert_float(row.get('BAGR150'))
                metrics.bachelors_grad_rate_200 = safe_convert_float(row.get('BAGR200'))
                
                metrics.certificate_revised_cohort = safe_convert(row.get('L4REVCT'))
                metrics.certificate_completed_100pct = safe_convert(row.get('L4NC100'))
                metrics.certificate_completed_150pct = safe_convert(row.get('L4NC150'))
                metrics.certificate_completed_200pct = safe_convert(row.get('L4NC200'))
                metrics.certificate_still_enrolled = safe_convert(row.get('L4STEND'))
                
                metrics.certificate_grad_rate_100 = safe_convert_float(row.get('L4GR100'))
                metrics.certificate_grad_rate_150 = safe_convert_float(row.get('L4GR150'))
                metrics.certificate_grad_rate_200 = safe_convert_float(row.get('L4GR200'))

                # Add or update the record
                if metrics.id is None:
                    db.session.add(metrics)
                
                success_count += 1

            except Exception as e:
                error_count += 1
                print(f"Error processing row: {str(e)}")
                continue

        # Commit all successful additions
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Successfully imported {success_count} IPEDS graduation metrics. {error_count} errors.'
        }

    except Exception as e:
        db.session.rollback()
        print(f"Top level error: {str(e)}")
        return {
            'success': False,
            'error': f'Error importing IPEDS graduation metrics: {str(e)}'
        }
