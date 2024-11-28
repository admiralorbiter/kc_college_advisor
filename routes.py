from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Institution, InstitutionLevel, InstitutionControl, HighestDegree, InstitutionLocale, InstitutionStatus, Pset4Flag, InstitutionCategory, InstitutionSizeClassification, CarnegieClassification
import pandas as pd
import csv
import io
import os

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
    
    # Create the sort expression
    sort_column = getattr(Institution, sort_by)
    if direction == 'desc':
        sort_column = sort_column.desc()
    
    # Start with base query
    query = Institution.query.filter(Institution.state.in_(['MO', 'KS']))
    
    # Apply name search if provided
    if name_search:
        query = query.filter(
            db.or_(
                Institution.name.ilike(f'%{name_search}%'),
                Institution.alias.ilike(f'%{name_search}%')
            )
        )
    
    # Apply location search if provided
    if location_search:
        query = query.filter(
            db.or_(
                Institution.city.ilike(f'%{location_search}%'),
                Institution.state.ilike(f'%{location_search}%'),
                Institution.county.ilike(f'%{location_search}%')
            )
        )
    
    # Apply sorting and get results
    institutions = query.order_by(sort_column).all()
    
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
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file and file.filename.endswith('.csv'):
            try:
                # Save the uploaded file temporarily
                temp_path = 'temp_upload.csv'
                file.save(temp_path)
                
                # Read the CSV file directly with pandas
                df = pd.read_csv(temp_path, encoding_errors='replace')
                
                # Delete the temporary file
                os.remove(temp_path)
                
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
                
                # After the existing mapping functions for level and control, add:
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

                # Add these conversions after the existing level and control mappings:
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
                
                # General clean_enum_value function for numeric enums
                def clean_enum_value(value, enum_class):
                    try:
                        if pd.isna(value) or value == '' or value == ' ' or value == '-2':
                            return enum_class.UNKNOWN
                        value = int(float(value))
                        return enum_class(value) if value in [e.value for e in enum_class] else enum_class.UNKNOWN
                    except (ValueError, TypeError):
                        return enum_class.UNKNOWN

                try:
                    for _, row in df.iterrows():
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
                
                return jsonify({
                    'success': True,
                    'message': message
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Error processing file: {str(e)}'
                })
    
    # GET request - show the upload form
    return render_template('institutions/import_institutions.html')

@app.route('/institutions/view/<int:id>')
def view_institution(id):
    institution = Institution.query.get_or_404(id)
    return render_template('institutions/view_institution.html', institution=institution)


