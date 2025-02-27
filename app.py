from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth, exceptions
import uuid
import requests
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from functools import lru_cache

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')
csrf = CSRFProtect(app)

# Initialize Firebase
cred = credentials.Certificate("fblc/firebaseconfig.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Firebase REST API configuration
load_dotenv()
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
if not FIREBASE_API_KEY:
    raise ValueError("FIREBASE_API_KEY not found in environment variables")

class User(UserMixin):
    def __init__(self, uid, email, name, language):
        self.id = uid
        self.email = email
        self.name = name
        self.language = language

@login_manager.user_loader
def load_user(user_id):

    try:
        user_doc = db.collection('users').document(user_id).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return User(user_id, user_data['email'], user_data['name'], user_data['language'])
    except Exception as e:
        print(f"Error loading user: {e}")
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = FlaskForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = request.form.get('email')
            password = request.form.get('password')
            
            try:
                # Authenticate with Firebase REST API
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
                data = {
                    "email": email,
                    "password": password,
                    "returnSecureToken": True
                }
                response = requests.post(url, json=data)
                
                if response.status_code == 200:
                    id_token = response.json().get('idToken')
                    try:
                        decoded_token = auth.verify_id_token(id_token)
                        uid = decoded_token['uid']
                        user_doc = db.collection('users').document(uid).get()
                        
                        if user_doc.exists:
                            user_data = user_doc.to_dict()
                            user = User(uid, user_data['email'], user_data['name'], user_data['language'])
                            login_user(user)
                            return redirect(url_for('dashboard'))
                        else:
                            flash('User data not found.')
                    except exceptions.FirebaseError as e:
                        flash('Authentication failed.')
                else:
                    flash('Invalid email or password.')
            except Exception as e:
                flash('An error occurred during login.')
                print(f"Login error: {e}")
            
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = FlaskForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name')
            language = request.form.get('language')
            
            try:
                # Create user using Firebase Authentication REST API
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
                data = {
                    "email": email,
                    "password": password,
                    "returnSecureToken": True
                }
                print(f"Sending registration request for {email}...")  # Debug print
                response = requests.post(url, json=data)
                
                # Print the response from Firebase for debugging
                print(f"Response status code: {response.status_code}")
                print(f"Response JSON: {response.json()}")
                
                if response.status_code == 200:
                    user_data = response.json()
                    uid = user_data['localId']  # Get the UID of the created user
                    print(f"User created successfully with UID: {uid}")  # Debug print
                    
                    # Store additional user data in Firestore
                    db.collection('users').document(uid).set({
                        'email': email,
                        'name': name,
                        'language': language,
                        'created_at': firestore.SERVER_TIMESTAMP
                    })
                    print(f"User data saved to Firestore.")  # Debug print
                    
                    # Log the user in
                    new_user = User(uid, email, name, language)
                    login_user(new_user)
                    print(f"User logged in and redirected to dashboard.")  # Debug print
                    return redirect(url_for('dashboard'))
                else:
                    error_message = response.json().get('error', {}).get('message', 'Unknown error')
                    print(f"Registration failed. Error message from Firebase: {error_message}")  # Debug print
                    flash('Registration failed. Please try again. Error: ' + str(error_message))
            
            except Exception as e:
                print(f"An error occurred during registration: {e}")  # Debug print
                flash('An error occurred during registration.')
            
    return render_template('auth/register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash('Successfully logged out.')
    except Exception as e:
        flash('Error during logout.')
        print(f"Logout error: {e}")
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Process appointments into dictionaries
    appointments_query = db.collection('appointments').where('user_id', '==', current_user.id).order_by('date').limit(5).stream()
    appointments = [appt.to_dict() for appt in appointments_query]
    
    # Process health data
    health_data_query = db.collection('health_data').where('user_id', '==', current_user.id).order_by('date', direction=firestore.Query.DESCENDING).limit(1).stream()
    health_data_doc = next(health_data_query, None)
    health_data = health_data_doc.to_dict() if health_data_doc else None
    
    return render_template('dashboard.html', appointments=appointments, health_data=health_data)

@app.route('/appointments')
@login_required
def appointments():
    # Fetch appointments and convert them to dictionaries
    appointments_query = db.collection('appointments').where('user_id', '==', current_user.id).order_by('date').stream()
    appointments = [appt.to_dict() for appt in appointments_query]  # Convert DocumentSnapshots to dictionaries
    
    return render_template('appointments.html', appointments=appointments)

@app.route('/find_providers')
@login_required
def find_providers():
    providers = db.collection('providers').where('verified', '==', True).stream()
    return render_template('find_providers.html', providers=providers)
    # return render_template('find_providers.html')

@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    form = FlaskForm()  # Create form instance
    if request.method == 'POST':
        if form.validate_on_submit():  # Validate CSRF token
            doctor_name = request.form.get('doctor_name')
            appointment_type = request.form.get('appointment_type')
            date_str = request.form.get('date')
            cost = float(request.form.get('cost', 0))
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            
            db.collection('appointments').add({
                'user_id': current_user.id,
                'doctor_name': doctor_name,
                'type': appointment_type,
                'date': date,
                'cost': cost
            })
            flash('Appointment booked successfully!')
            return redirect(url_for('appointments'))
        else:
            flash('Invalid form submission. Please try again.')
    
    providers = db.collection('providers').where('verified', '==', True).stream()
    return render_template('book_appointment.html', form=form, providers=providers)  # Pass form to template

@app.route('/health_tracker')
@login_required
def health_tracker():
    form = FlaskForm()
    health_entries = []
    
    # Get raw data from Firestore
    docs = db.collection('health_data')\
             .where('user_id', '==', current_user.id)\
             .order_by('date', direction=firestore.Query.DESCENDING)\
             .limit(7)\
             .stream()
    
    # Process dates for template
    for doc in docs:
        data = doc.to_dict()
        # Convert Firestore timestamp to Python datetime if needed
        date = data['date']  # Firestore returns a datetime object
        health_entries.append({
            'date': date.strftime('%Y-%m-%d'),  # Format as string
            'steps': data['steps'],
            'calories': data['calories'],
            'sleep_hours': data['sleep_hours']
        })
    
    health_data_query = db.collection('health_data').where('user_id', '==', current_user.id).order_by('date', direction=firestore.Query.DESCENDING).limit(1).stream()
    health_data_doc = next(health_data_query, None)
    health_data = health_data_doc.to_dict() if health_data_doc else None

    return render_template('health_tracker.html', 
                         form=form, 
                         health_data=health_entries, health=health_data)

@app.route('/add_health_data', methods=['POST'])
@login_required
def add_health_data():
    form = FlaskForm()
    
    if form.validate_on_submit():
        # Use datetime.now() to get a datetime object
        date = datetime.now()  # This is a datetime.datetime object
        
        steps = request.form.get('steps', type=int)
        calories = request.form.get('calories', type=int)
        sleep_hours = request.form.get('sleep_hours', type=float)
        
        # Add document to Firestore
        db.collection('health_data').add({
            'user_id': current_user.id,
            'date': date,  # datetime.datetime object
            'steps': steps,
            'calories': calories,
            'sleep_hours': sleep_hours
        })
        flash('Health data added successfully!')
    else:
        flash('Invalid form submission. Please try again.')
        
    return redirect(url_for('health_tracker'))

@app.route('/api/health_data')
@login_required
def api_health_data():
    days = request.args.get('days', default=7, type=int)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    health_data = db.collection('health_data').where('user_id', '==', current_user.id).where('date', '>=', start_date).where('date', '<=', end_date).order_by('date').stream()
    
    data = [{
        'date': item.to_dict()['date'].strftime('%Y-%m-%d'),
        'steps': item.to_dict()['steps'],
        'calories': item.to_dict()['calories'],
        'sleep_hours': item.to_dict()['sleep_hours']
    } for item in health_data]
    
    return jsonify(data)

@app.route('/add_business', methods=['GET', 'POST'])
@login_required
def add_business():
    form = FlaskForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = request.form.get('name')
            specialty = request.form.get('specialty')
            address = request.form.get('address')
            phone = request.form.get('phone')
            
            business_id = str(uuid.uuid4())
            db.collection('providers').document(business_id).set({
                'name': name,
                'specialty': specialty,
                'address': address,
                'phone': phone,
                'owner_id': current_user.id,
                'verified': False
            })
            flash('Business added successfully! It will be visible after verification.')
            return redirect(url_for('dashboard'))
    
    return render_template('add_business.html', form=form)

@app.route('/api/providers')
@login_required
def api_providers():
    providers = db.collection('providers').where('verified', '==', True).stream()
    # Get user's address from their profile
    user_lat = request.args.get('lat')
    user_lng = request.args.get('lng')
    user_coords = (float(user_lat), float(user_lng)) if user_lat and user_lng else None
    
    # Use lru_cache to avoid repeated geocoding for the same address
    @lru_cache(maxsize=100)
    def geocode_address(address):
        if not address:
            return None
        try:
            geolocator = Nominatim(user_agent="health-app")
            location = geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
            return None
        except:
            return None
    
    provider_list = [{
        'id': doc.id,
        'name': doc.to_dict()['name'],
        'specialty': doc.to_dict()['specialty'],
        'distance': round(geodesic(user_coords, geocode_address(doc.to_dict().get('address', ''))).kilometers, 1) if user_coords and geocode_address(doc.to_dict().get('address', '')) else None,
        'address': doc.to_dict()['address'],
    } for doc in providers]
    print(provider_list)
    return jsonify(provider_list)

@app.route('/api/provider/<provider_id>')
@login_required
def api_provider(provider_id):
    doc = db.collection('providers').document(provider_id).get()
    if doc.exists:
        provider_data = doc.to_dict()
        return jsonify({
            'id': doc.id,
            'name': provider_data.get('name'),
            'specialty': provider_data.get('specialty'),
            'address': provider_data.get('address'),
            'phone': provider_data.get('phone')
        })
    return jsonify({'error': 'Provider not found'}), 404

@app.route('/admin')
@login_required
def admin():
    # Retrieve provider documents and convert them to a list of dictionaries,
    # including each document's id.
    providers = []
    for provider_doc in db.collection('providers').stream():
        provider_data = provider_doc.to_dict()
        provider_data['id'] = provider_doc.id
        providers.append(provider_data)
    return render_template("admin.html", providers=providers)

@app.route('/api/verify-provider/<provider_id>', methods=['POST'])
@csrf.exempt
def verify_provider(provider_id):
    # Add admin check here
    # user_doc = db.collection('users').document(current_user.id).get()
    # if not user_doc.exists or not user_doc.to_dict().get('is_admin', False):
    #     return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    try:
        provider_ref = db.collection('providers').document(provider_id)
        provider = provider_ref.get()
        
        if provider.exists:
            provider_ref.update({'verified': True})
            return jsonify({'success': True, 'message': 'Provider verified successfully'})
        else:
            return jsonify({'success': False, 'message': 'Provider not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False)