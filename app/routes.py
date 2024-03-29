from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, mongo
from app.forms import RegistrationForm, LoginForm
from app.models import User
from datetime import datetime

# User authentication routes
# ...

@app.route('/')
def index():
    return render_template('index.html')

# User authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data, role=form.role.data)
        mongo.db.users.insert_one(user.to_dict())
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({'email': form.email.data})
        if user and User(user['email'], user['password_hash'], user['role']).check_password(form.password.data):
            user_obj = User(user['email'], user['password_hash'], user['role'])
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    if request.method == 'POST':
        appointment_data = {
            'patient_id': request.form['patient_id'],
            'doctor_id': current_user.id,
            'date': datetime.strptime(request.form['date'], '%Y-%m-%d'),
            'time': request.form['time'],
            'reason': request.form['reason']
        }
        mongo.db.appointments.insert_one(appointment_data)
        flash('Appointment scheduled successfully!', 'success')
    appointments = mongo.db.appointments.find()
    return render_template('appointments.html', appointments=appointments)

# Patient routes
@app.route('/patients', methods=['GET', 'POST'])
@login_required
def patients():
    patients = mongo.db.patients.find()
    return render_template('patient.html', patients=patients)

@app.route('/patient/<patient_id>', methods=['GET'])
@login_required
def patient_details(patient_id):
    patient = mongo.db.patients.find_one({'_id': patient_id})
    history = mongo.db.patient_history.find({'patient_id': patient_id})
    family = mongo.db.patient_family.find({'patient_id': patient_id})
    return render_template('patient_details.html', patient=patient, history=history, family=family)

# Patient health history routes
@app.route('/patient/<patient_id>/history', methods=['GET', 'POST'])
@login_required
def patient_history(patient_id):
    if request.method == 'POST':
        history_data = {
            'patient_id': patient_id,
            'condition': request.form['condition'],
            'diagnosis': request.form['diagnosis'],
            'treatment': request.form['treatment'],
            'date': datetime.strptime(request.form['date'], '%Y-%m-%d')
        }
        mongo.db.patient_history.insert_one(history_data)
        flash('Health history added successfully!', 'success')
    history = mongo.db.patient_history.find({'patient_id': patient_id})
    return render_template('patient_history.html', history=history, patient_id=patient_id)

# Patient family tracking routes
@app.route('/patient/<patient_id>/family', methods=['GET', 'POST'])
@login_required
def patient_family(patient_id):
    if request.method == 'POST':
        family_data = {
            'patient_id': patient_id,
            'name': request.form['name'],
            'relation': request.form['relation'],
            'age': int(request.form['age']),
            'medical_history': request.form['medical_history']
        }
        mongo.db.patient_family.insert_one(family_data)
        flash('Family member added successfully!', 'success')
    family = mongo.db.patient_family.find({'patient_id': patient_id})
    return render_template('patient_family.html', family=family, patient_id=patient_id)

# Appointment routes
# ...

# Laboratory tests routes
@app.route('/lab_tests', methods=['GET', 'POST'])
@login_required
def lab_tests():
    if request.method == 'POST':
        test_data = {
            'patient_id': request.form['patient_id'],
            'test_type': request.form['test_type'],
            'ordered_by': current_user.id,
            'order_date': datetime.utcnow(),
            'results': None
        }
        mongo.db.lab_tests.insert_one(test_data)
        flash('Laboratory test ordered successfully!', 'success')
    tests = mongo.db.lab_tests.find()
    return render_template('lab_tests.html', tests=tests)

@app.route('/lab_test/<test_id>', methods=['GET', 'POST'])
@login_required
def lab_test_details(test_id):
    if request.method == 'POST':
        test_results = request.form['results']
        mongo.db.lab_tests.update_one({'_id': test_id}, {'$set': {'results': test_results}})
        flash('Test results updated successfully!', 'success')
    test = mongo.db.lab_tests.find_one({'_id': test_id})
    return render_template('lab_test_details.html', test=test)

# Prescription routes
@app.route('/prescriptions', methods=['GET', 'POST'])
@login_required
def prescriptions():
    if request.method == 'POST':
        prescription_data = {
            'patient_id': request.form['patient_id'],
            'medication': request.form['medication'],
            'dosage': request.form['dosage'],
            'instructions': request.form['instructions'],
            'prescribed_by': current_user.id,
            'prescribed_date': datetime.utcnow()
        }
        mongo.db.prescriptions.insert_one(prescription_data)
        flash('Prescription added successfully!', 'success')
    prescriptions = mongo.db.prescriptions.find()
    return render_template('prescriptions.html', prescriptions=prescriptions)

# Analytical reporting routes
@app.route('/reports', methods=['GET'])
@login_required
def reports():
    # Implement analytical reporting logic here
    # Example: Get patient count by age group
    patient_age_groups = mongo.db.patients.aggregate([
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
@login_required
def search():
    if request.method == 'POST':
        query = request.form['query']
        patients = mongo.db.patients.find({'$text': {'$search': query}})
        return render_template('search.html', patients=patients, query=query)
    return render_template('search.html')