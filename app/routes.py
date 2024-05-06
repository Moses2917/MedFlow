from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.forms import RegistrationForm, LoginForm
from app.models import User
from datetime import datetime
from bson.objectid import ObjectId

# User authentication routes

#db_operations = db.<COLLECTION_NAME>

@app.route('/')
def index():
    appointments = ''
    if session.get('user', None):
        email = session['user'].get('email')
        if email:
            cursor = db.appointments.find({'doctor': email})
            appointments = [doc for doc in cursor]
    return render_template('index.html',appointments=appointments)

# User authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data, role=form.role.data)
        if db.users.find_one({'email': form.email.data}):#checks to see if that email already exists as a registered user
            flash('Please choose another email that one is already taken','warning')
        else:
            db.users.insert_one(user.to_dict())
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.users.find_one({'email': form.email.data})
        if user and User(user['email'], user['password_hash'], user['role']).check_password(request.form.get("password")):
            user_obj = User(user['email'], user['password_hash'], user['role'])
            session['_user_id'] = str(user["_id"])
            session["user"] = user_obj.to_dict()
            # login_user(user_obj,remember=True)
            # user_obj.
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
# @login_required
def logout():
    logout_user()
    session["user"] = None
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/appointments', methods=['GET', 'POST'])
# @login_required
def appointments():
    appointments = ""
    patient_list = None
    if session.get('user', None):
        email = session['user'].get('email')  
        if email:
            #This is to get the patients
            cursor = db.patients.find({"doctor": email})
            patient_list = [doc for doc in cursor]
    if request.method == 'POST':
        if session.get('user', None):
            email = session['user'].get('email')
            if email:
                appointment_data = {
                    'patient_id': request.form['patient_id'],
                    'doctor': session["user"]["email"],
                    'date': datetime.strptime(request.form['date'], '%Y-%m-%d'),
                    'time': request.form['time'],
                    'reason': request.form['reason']
                }
                db.appointments.insert_one(appointment_data)
                flash('Appointment scheduled successfully!', 'success')
    if session.get('user', None):
        email = session['user'].get('email')
        if email:
            cursor = db.appointments.find({'doctor': email})
            appointments = [doc for doc in cursor]
    return render_template('appointments.html', appointments=appointments, patients=patient_list)

# Patient routes
@app.route('/patients', methods=['GET', 'POST'])
# @login_required
def patients():
    patient_list = None
    if session.get('user', None):
        email = session['user'].get('email')  
        if email:
            cursor = db.patients.find({"doctor": email})
            patient_list = [doc for doc in cursor]
    return render_template('patient.html', patients=patient_list)

@app.route('/NewPatient', methods=['GET','POST']) #could possibly be used as a add/edit
def add_patient():
    if request.method == 'POST':
        patient = {
            'name': request.form.get('name'),
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'contact': request.form.get('contact'),
            'doctor': session['user']['email'],
            'comments': request.form.get('comments')
        }
        db.patients.insert_one(patient)
        return redirect(url_for('patients'))
    return render_template('add_patient.html')

@app.route('/patient_details/<patient_id>', methods=['GET'])
# @login_required
def patient_details(patient_id):
    
    patient = patient_id
    history = db.patient_history.find({'patient_id': patient_id})
    family = db.patient_family.find({'patient_id': patient_id})
    appointments = ""
    if session.get('user', None):
        email = session['user'].get('email')
        if email:
            #Sets the currently active patient
            session['patient'] = db.patients.find_one({
                "doctor": email,
                "name": patient_id
                })
            
            #Converting the objectid object to a str
            session['patient']['_id'] = str(session['patient']['_id'])
            
            cursor = db.appointments.find({
                "doctor": email,
                "patient_id": patient_id
                })
            appointments = [doc for doc in cursor]
    return render_template('patient_details.html', patient=patient, history=history, family=family, appointments=appointments)

# Patient health history routes
@app.route('/patient/<patient_id>/history', methods=['GET', 'POST'])
# @login_required
def patient_history(patient_id):
    if request.method == 'POST':
        history_data = {
            'patient_id': patient_id,
            'condition': request.form['condition'],
            'diagnosis': request.form['diagnosis'],
            'treatment': request.form['treatment'],
            'date': datetime.strptime(request.form['date'], '%Y-%m-%d')
        }
        db.patient_history.insert_one(history_data)
        flash('Health history added successfully!', 'success')
    history = db.patient_history.find({'patient_id': patient_id})
    return render_template('patient_history.html', history=history, patient_id=patient_id)

# Patient family tracking routes
@app.route('/patient/<patient_id>/family', methods=['GET', 'POST'])
# @login_required
def patient_family(patient_id):
    if request.method == 'POST':
        family_data = {
            'patient_id': patient_id,
            'name': request.form['name'],
            'relation': request.form['relation'],
            'age': int(request.form['age']),
            'medical_history': request.form['medical_history']
        }
        db.patient_family.insert_one(family_data)
        flash('Family member added successfully!', 'success')
    family = db.patient_family.find({'patient_id': patient_id})
    return render_template('patient_family.html', family=family, patient_id=patient_id)

@app.route('/edit_details', methods=['GET','POST']) #could possibly be used as a add/edit
def edit_details():
    if request.method == 'POST':
        patient = {
            'name': request.form.get('name', session['patient']['name']),
            'age': request.form.get('age', session['patient']['age']),
            'gender': request.form.get('gender', session['patient']['gender']),
            'contact': request.form.get('contact', session['patient']['contact']),
            'comments': request.form.get('comments', session['patient']['contact']),
            'doctor': session['user']['email']
        }
        db.patients.find_one_and_replace({
            '_id': ObjectId(session['patient']['_id'])
                },
            patient
            )
        return redirect(url_for('patients'))
    return render_template('edit_details.html')

# Laboratory tests routes
@app.route('/lab_tests', methods=['GET', 'POST'])
# @login_required
def lab_tests():
    tests = ""
    if request.method == 'POST':
        test_data = {
            'patient_id': session['patient']['name'],
            'test_type': request.form['test_type'],
            'ordered_by': session["user"]["email"],
            'order_date': datetime.strftime(datetime.now(), '%m-%d-%Y'),
            'results': None
        }
        db.lab_tests.insert_one(test_data)
        flash('Laboratory test ordered successfully!', 'success')
    if session.get('user', None):
        email = session['user'].get('email')
        if email:
            cursor = db.lab_tests.find({
                "ordered_by": email,
                "patient_id": session['patient']['name']
                })
            tests = [doc for doc in cursor]
    # tests = db.lab_tests.find()
    return render_template('lab_tests.html', tests=tests)

@app.route('/lab_test/<test_id>', methods=['GET', 'POST'])
# @login_required
def lab_test_details(test_id):
    if request.method == 'POST':
        test_results = request.form['results']
        db.lab_tests.update_one({'_id': test_id}, {'$set': {'results': test_results}})
        flash('Test results updated successfully!', 'success')
    test = db.lab_tests.find_one({'_id': test_id})
    return render_template('lab_test_details.html', test=test)

# Prescription routes
@app.route('/prescriptions', methods=['GET', 'POST'])
# @login_required
def prescriptions():
    prescriptions = ""
    if request.method == 'POST':
        prescription_data = {
            'patient_id': session['patient']['name'],
            'medication': request.form['medication'],
            'dosage': request.form['dosage'],
            'instructions': request.form['instructions'],
            'reason': request.form['reason'],
            'prescribed_by': session['user']['email'],
            'prescribed_date': datetime.now()
        }
        db.prescriptions.insert_one(prescription_data)
        flash('Prescription added successfully!', 'success')
        
    if session.get('user', None):
        email = session['user'].get('email')
        if email:
            cursor = db.prescriptions.find({
                "prescribed_by": email,
                "patient_id": session['patient']['name']
                })
            prescriptions = [doc for doc in cursor]
    # prescriptions = db.prescriptions.find()
    return render_template('prescriptions.html', prescriptions=prescriptions)

# Analytical reporting routes
@app.route('/reports', methods=['GET'])
# @login_required
def reports():
    # Implement analytical reporting logic here
    # Example: Get patient count by age group
    patient_age_groups = db.patients.aggregate([
        {'$bucket': {
            'groupBy': '$age',
            'boundaries': [0, 18, 30, 45, 60, 120],
            'default': 'Other',
            'output': {
                'total': {'$sum': 1},
                'age_group': {'$push': '$age'}
            }
        }},
        {'$project': {
            '_id': 0,
            'age_group': {'$arrayElemAt': ['$age_group', 0]},
            'total': 1
        }}
    ])
    return render_template('reports.html', age_groups=patient_age_groups)

# Search functionality
@app.route('/search', methods=['GET', 'POST'])
# @login_required
def search():
    if request.method == 'POST':
        query = request.form['query']
        patients = db.patients.find({'$text': {'$search': query}})
        return render_template('search.html', patients=patients, query=query)
    return render_template('search.html')

#delete patient
@app.route('/delete_patient/<patient_id>', methods=['GET'])
def delete_patient(patient_id):
    if session.get('user', None):
        email = session['user'].get('email')
        if email:
            if patient_id:
                
                db.patients.delete_one({
                    "doctor": email,
                    "name": patient_id
                    })
            else:
                flash('Patient NOT deleted successfully!', 'error')
            
            flash('Patient deleted successfully!', 'success')
    return redirect(url_for('patients'))  # Redirect to the patients page after deletion

#Delete Appointment
@app.route('/delete_appointment/<appointment>', methods=['GET','POST'])
def delete_appointment(appointment):
    
    item_to_delete = ObjectId(appointment)
    # item_to_delete = appointment
    if item_to_delete:
        deleted_appoitment = db.appointments.find_one_and_delete({
            '_id':item_to_delete
            })
        return redirect(url_for('appointments'))
    else:
        return "Not Found", 404

