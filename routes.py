from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Institution
import pandas as pd
import csv
import io

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
            # List of encodings to try
            encodings = ['UTF-8', 'UTF-8-SIG', 'ISO-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    # Read the file content
                    content = file.read()
                    # Reset file pointer for potential next iteration
                    file.seek(0)
                    
                    # Try to decode with current encoding
                    decoded_content = content.decode(encoding)
                    stream = io.StringIO(decoded_content, newline=None)
                    df = pd.read_csv(stream)
                    
                    # If we get here, the encoding worked
                    print(f"Successfully decoded with {encoding}")
                    
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
                        'DISAURL': 'disability_services_url'
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
                                disability_services_url=row['disability_services_url']
                            )
                            db.session.add(institution)
                            success_count += 1
                        except Exception as e:
                            error_count += 1
                            continue
                    
                    # Commit all successful additions
                    db.session.commit()
                    
                    message = f'Successfully imported {success_count} institutions.'
                    if error_count > 0:
                        message += f' {error_count} records had errors and were skipped.'
                    
                    return jsonify({
                        'success': True,
                        'message': message
                    })
                    
                except UnicodeDecodeError:
                    # If this encoding didn't work, try the next one
                    continue
                except Exception as e:
                    # Handle other errors
                    db.session.rollback()
                    return jsonify({
                        'success': False,
                        'error': f'Error processing file with {encoding}: {str(e)}'
                    })
                
                # If we successfully processed the file, break the loop
                break
            else:
                # If we've tried all encodings and none worked
                return jsonify({
                    'success': False,
                    'error': 'Could not decode file with any supported encoding'
                })
    
    # GET request - show the upload form
    return render_template('institutions/import_institutions.html')

@app.route('/institutions/view/<int:id>')
def view_institution(id):
    institution = Institution.query.get_or_404(id)
    return render_template('institutions/view_institution.html', institution=institution)


