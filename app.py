from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
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
import random
import string

# Matplotlib imports
import base64
from io import BytesIO
from matplotlib.figure import Figure

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')
csrf = CSRFProtect(app)

# Initialize Firebase
cred = credentials.Certificate("firebaseconfig.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Firebase REST API configuration
load_dotenv()
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
if not FIREBASE_API_KEY:
    raise ValueError("FIREBASE_API_KEY not found in environment variables")

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY not found in environment variables")

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
    # Process appointments into dictionaries with formatted dates
    appointments_query = (db.collection('appointments')
                         .where('user_id', '==', current_user.id)
                         .order_by('date')
                         .limit(5)
                         .stream())
    
    appointments = []
    for appt in appointments_query:
        appt_data = appt.to_dict()
        appt_data['id'] = appt.id
        
        # Format the date and time
        try:
            # Handle date
            date = appt_data.get('date')
            if isinstance(date, datetime):
                appt_data['formatted_date'] = date.strftime('%B %d, %Y')
            elif isinstance(date, str):
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                appt_data['formatted_date'] = date_obj.strftime('%B %d, %Y')
            else:
                appt_data['formatted_date'] = 'Date not available'

            # Handle time
            time = appt_data.get('time')
            if time:
                time_obj = datetime.strptime(time, '%H:%M')
                appt_data['formatted_time'] = time_obj.strftime('%I:%M %p')
            else:
                appt_data['formatted_time'] = 'Time not available'

        except ValueError as e:
            print(f"Date formatting error: {e}")
            appt_data['formatted_date'] = 'Invalid date format'
            appt_data['formatted_time'] = 'Invalid time format'
        
        appointments.append(appt_data)

    # Fetch latest health news
    try:
        response = requests.get(
            f"https://newsapi.org/v2/everything?q=health&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        )
        response.raise_for_status()  # Raises an exception for HTTP errors
        news_data = response.json()
        articles = news_data.get('articles', [])
        latest_news = articles[:5]  # Limit to top 5 articles

    except Exception as e:
        print(f"Error fetching news: {e}")
        latest_news = []  # Fallback to empty list on failure

    return render_template('dashboard.html',
                           appointments=appointments,
                           current_time=datetime.now(),
                           latest_news=latest_news)



@app.route('/appointments')
@login_required
def appointments():
    # Fetch appointments with provider details
    appointments_query = (db.collection('appointments')
                        .where('user_id', '==', current_user.id)
                        .order_by('date')
                        .stream())
    
    appointments_list = []
    for appt in appointments_query:
        appt_data = appt.to_dict()
        appt_data['id'] = appt.id
        
        # Get provider details
        if 'provider_id' in appt_data:
            provider_doc = db.collection('providers').document(appt_data['provider_id']).get()
            if provider_doc.exists:
                provider_data = provider_doc.to_dict()
                appt_data['provider_name'] = provider_data.get('name')
                appt_data['provider_specialty'] = provider_data.get('specialty')
                appt_data['provider_address'] = provider_data.get('address')
                appt_data['provider_phone'] = provider_data.get('phone')
        
        # Format the date
        try:
            if isinstance(appt_data.get('date'), str):
                # If date is a string, parse it
                date_obj = datetime.strptime(appt_data['date'], '%Y-%m-%d')
                appt_data['formatted_date'] = date_obj.strftime('%B %d, %Y')
            elif isinstance(appt_data.get('date'), datetime):
                # If date is already a datetime object
                appt_data['formatted_date'] = appt_data['date'].strftime('%B %d, %Y')
            else:
                appt_data['formatted_date'] = 'Date not available'
        except ValueError:
            appt_data['formatted_date'] = 'Invalid date format'
        
        # Format the time
        try:
            if isinstance(appt_data.get('time'), str):
                time_obj = datetime.strptime(appt_data['time'], '%H:%M')
                appt_data['formatted_time'] = time_obj.strftime('%I:%M %p')
            else:
                appt_data['formatted_time'] = appt_data.get('time', 'Time not available')
        except ValueError:
            appt_data['formatted_time'] = 'Invalid time format'
            
        appointments_list.append(appt_data)
    
    return render_template('appointments.html', 
                         appointments=appointments_list,
                         current_time=datetime.now())

@app.route('/find_providers')
@login_required
def find_providers():
    providers = db.collection('providers').where('verified', '==', True).stream()
    # Get provider data
    providers_list = []
    for provider in providers:
        providers_list.append(provider.to_dict())

    # Count specialties
    specialty_counts = {}
    for provider in providers_list:
        specialty = provider.get('specialty')
        if specialty:
            specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
    
    # Sort specialties by count and get top 5
    top_specialties_query = sorted(
        specialty_counts.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:5]
    
    # Convert query results to a list of specialty names
    top_specialties = [specialty for specialty, count in top_specialties_query if specialty]
    
    # Add some default specialties if the database doesn't have enough data
    default_specialties = ['Primary Care', 'Cardiology', 'Dermatology', 'Pediatrics', 'Orthopedics']
    if len(top_specialties) < 5:
        remaining_defaults = [s for s in default_specialties if s not in top_specialties]
        top_specialties.extend(remaining_defaults[:5-len(top_specialties)])
    
    return render_template('find_providers.html', top_specialties=top_specialties, providers=providers_list)

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
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)
    
    # Set start date to midnight and end date to 23:59:59
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Query health data for the current user
    health_data = db.collection('health_data')\
        .where('user_id', '==', current_user.id)\
        .where('date', '>=', start_date)\
        .where('date', '<=', end_date)\
        .order_by('date')\
        .stream()
    
    # Format data for the graph
    data = []
    for item in health_data:
        item_data = item.to_dict()
        data.append({
            'date': item_data['date'].strftime('%Y-%m-%d'),
            'steps': item_data.get('steps', 0),
            'calories': item_data.get('calories', 0),
            'sleep_hours': item_data.get('sleep_hours', 0)
        })
    
    return jsonify(data)

@app.route('/add_business', methods=['GET', 'POST'])
@login_required
def add_business():
    form = FlaskForm()
    here_api_key = "lUFTE1skWuIcrj_s0wCZbbM2KWcgT2JnJcKGWHFi4WA"
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Add new business
            db.collection('providers').add({
                'name': request.form.get('name'),
                'specialty': request.form.get('specialty'),
                'address': request.form.get('address'),
                'phone': request.form.get('phone'),
                'verified': False,  # New businesses start unverified
                'owner_id': current_user.id,
                'created_at': firestore.SERVER_TIMESTAMP
            })
            flash('Business added successfully! It will be reviewed for verification.')
            return redirect(url_for('manage_business'))
        except Exception as e:
            flash(f'Error adding business: {e}')
    
    return render_template('add_business.html', form=form, here_api_key=here_api_key)

@app.route('/api/providers')
@login_required
def api_providers():
    specialty = request.args.get('specialty', None)
    query = db.collection('providers').where('verified', '==', True)
    
    if specialty:
        query = query.where('specialty', '==', specialty)
    
    providers = query.stream()
    
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
    
    provider_list = []
    for doc in providers:
        provider_data = doc.to_dict()
        distance = None
        
        if user_coords and geocode_address(provider_data.get('address', '')):
            distance = round(geodesic(
                user_coords, 
                geocode_address(provider_data.get('address', ''))
            ).kilometers, 1)
        
        provider_list.append({
            'id': doc.id,
            'name': provider_data.get('name', ''),
            'specialty': provider_data.get('specialty', ''),
            'distance': distance,
            'address': provider_data.get('address', ''),
            'phone': provider_data.get('phone', ''),
            # Include inclusive care options
            'lgbtq_friendly': provider_data.get('lgbtq_friendly', False),
            'disability_accessible': provider_data.get('disability_accessible', False),
            'cultural_responsive': provider_data.get('cultural_responsive', False),
            'language_services': provider_data.get('language_services', False),
            'sliding_scale': provider_data.get('sliding_scale', False),
            'trauma_informed': provider_data.get('trauma_informed', False),
            # Include loyalty program data
            'loyalty_enabled': provider_data.get('loyalty_enabled', False),
            'loyalty_visits_required': provider_data.get('loyalty_visits_required', 10),
            'loyalty_reward': provider_data.get('loyalty_reward', '')
        })
    
    return jsonify(provider_list)

@app.route('/api/provider/<provider_id>')
@login_required
def api_provider(provider_id):
    doc = db.collection('providers').document(provider_id).get()
    if doc.exists:
        provider_data = doc.to_dict()
        
        # Get coordinates using the cached geocoding function
        @lru_cache(maxsize=100)
        def geocode_address(address):
            if not address:
                return None
            try:
                geolocator = Nominatim(user_agent="health-app")
                location = geolocator.geocode(address)
                if location:
                    return {
                        'lat': location.latitude,
                        'lng': location.longitude
                    }
                return None
            except Exception as e:
                print(f"Geocoding error: {e}")
                return None

        # Get coordinates for the provider's address
        coordinates = geocode_address(provider_data.get('address'))

        return jsonify({
            'id': doc.id,
            'name': provider_data.get('name'),
            'specialty': provider_data.get('specialty'),
            'address': provider_data.get('address'),
            'phone': provider_data.get('phone'),
            'coordinates': coordinates  # Add coordinates to response
        })
    return jsonify({'error': 'Provider not found'}), 404

@app.route('/admin')
@login_required
def admin():
    """Admin dashboard for system management"""
    # Check if user is admin - only allow specific admin emails
    if current_user.email != 'root@gmail.com':
        flash('Unauthorized: Admin access required')
        return redirect(url_for('dashboard'))
    
    # Create form for CSRF protection
    form = FlaskForm()  # Add this line to create the form object
    
    # Get all providers for the admin panel
    providers = []
    providers_query = db.collection('providers').stream()
    for doc in providers_query:
        provider_data = doc.to_dict()
        provider_data['id'] = doc.id
        providers.append(provider_data)
    
    # Handle database cleanup request
    if request.method == 'POST' and form.validate_on_submit():
        collections_to_clean = request.form.getlist('collections')
        confirmation_code = request.form.get('confirmation_code')
        
        # Extra security - require a confirmation code
        if confirmation_code != "DELETE-CONFIRM":
            flash('Invalid confirmation code')
            return redirect(url_for('admin'))
        
        # Batch size for deletion (Firestore has limits)
        batch_size = 500
        total_deleted = 0
        
        for collection_name in collections_to_clean:
            try:
                deleted = delete_collection(db, collection_name, batch_size)
                total_deleted += deleted
                flash(f"Deleted {deleted} documents from {collection_name}")
            except Exception as e:
                flash(f"Error deleting from {collection_name}: {str(e)}")
        
        flash(f"Database cleanup completed. Total documents deleted: {total_deleted}")
        return redirect(url_for('admin'))
    
    # Get list of collections for the form
    collections = [
        'appointments',
        'health_data',
        'loyalty',
        'loyalty_redemptions',
        'loyalty_visits',
        'notifications',
        'providers',
        'reviews',
        # Don't include 'users' by default as it's risky to delete user accounts
    ]
    
    # Pass the form and collections to the template
    return render_template("admin.html", 
                          providers=providers, 
                          form=form,  # Add this line to pass the form
                          collections=collections)  # Add this line to pass collections

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

@app.route('/api/book-appointment', methods=['POST'])
@login_required
def api_book_appointment():
    try:
        data = request.get_json()
        
        # Create appointment document
        appointment_id = str(uuid.uuid4())
        db.collection('appointments').document(appointment_id).set({
            'user_id': current_user.id,
            'provider_id': data['provider_id'],
            'date': data['date'],
            'time': data['time'],
            'appointment_type': data['appointment_type'],
            'status': 'pending',
            'created_at': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            'status': 'success',
            'message': 'Appointment booked successfully',
            'appointment_id': appointment_id
        })
        
    except Exception as e:
        print(f"Error booking appointment: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to book appointment'
        }), 500

@app.route('/manage_business')
@login_required
def manage_business():
    # Get businesses owned by the current user
    businesses_query = (db.collection('providers')
                      .where('owner_id', '==', current_user.id)
                      .stream())
    
    businesses = []
    for business in businesses_query:
        business_data = business.to_dict()
        business_data['id'] = business.id
        businesses.append(business_data)
    
    return render_template('manage_business.html', businesses=businesses)

@app.route('/edit_business/<business_id>', methods=['GET', 'POST'])
@login_required
def edit_business(business_id):
    # Get business document
    business_doc = db.collection('providers').document(business_id).get()
    here_api_key = "lUFTE1skWuIcrj_s0wCZbbM2KWcgT2JnJcKGWHFi4WA"

    if not business_doc.exists:
        flash('Business not found.')
        return redirect(url_for('manage_business'))
    
    business_data = business_doc.to_dict()
    
    # Check if user is the owner
    if business_data.get('owner_id') != current_user.id:
        flash('You do not have permission to edit this business.')
        return redirect(url_for('manage_business'))
    
    form = FlaskForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Get loyalty program settings from form
            loyalty_enabled = 'loyalty_enabled' in request.form
            loyalty_visits_required = 10
            loyalty_reward = ''
            loyalty_message = ''
            
            if loyalty_enabled:
                loyalty_visits_required = int(request.form.get('loyalty_visits_required', 10))
                loyalty_reward = request.form.get('loyalty_reward', '')
                loyalty_message = request.form.get('loyalty_message', '')
                
                # Basic validation
                if loyalty_visits_required < 1:
                    loyalty_visits_required = 1
                elif loyalty_visits_required > 100:
                    loyalty_visits_required = 100
                    
                if not loyalty_reward.strip():
                    flash('Please provide a reward description for your loyalty program.')
                    return render_template('edit_business.html', form=form, business=business_data, here_api_key=here_api_key)
            
            # Update business data
            db.collection('providers').document(business_id).update({
                'name': request.form.get('name'),
                'specialty': request.form.get('specialty'),
                'address': request.form.get('address'),
                'phone': request.form.get('phone'),
                'updated_at': firestore.SERVER_TIMESTAMP,
                # Add loyalty settings
                'loyalty_enabled': loyalty_enabled,
                'loyalty_visits_required': loyalty_visits_required,
                'loyalty_reward': loyalty_reward,
                'loyalty_message': loyalty_message
            })
            
            flash('Business information and loyalty program updated successfully!')
            return redirect(url_for('manage_business'))
        except Exception as e:
            flash(f'Error updating business: {e}')
    
    return render_template('edit_business.html', form=form, business=business_data, here_api_key=here_api_key)

@app.route('/api/delete-business/<business_id>', methods=['DELETE'])
@login_required
def delete_business(business_id):
    try:
        # Check if business exists and belongs to user
        business_doc = db.collection('providers').document(business_id).get()
        if business_doc.exists:
            business_data = business_doc.to_dict()
            if business_data.get('owner_id') == current_user.id:
                # Delete the business
                db.collection('providers').document(business_id).delete()
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Unauthorized'}), 403
        else:
            return jsonify({'error': 'Business not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/business-appointments/<business_id>')
@login_required
def get_business_appointments(business_id):
    # Check if user owns this business
    business = db.collection('providers').document(business_id).get()
    
    if not business.exists:
        return jsonify({'error': 'Business not found'}), 404
        
    business_data = business.to_dict()
    if business_data.get('owner_id') != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get all appointments for this business
    appointments = []
    appointments_query = db.collection('appointments').where('provider_id', '==', business_id).stream()
    
    for appointment in appointments_query:
        appointment_data = appointment.to_dict()
        appointment_data['id'] = appointment.id
        
        # Format dates for API consumption
        if isinstance(appointment_data.get('date'), datetime):
            appointment_data['date'] = appointment_data['date'].isoformat()
            
        # Get client information if available
        if appointment_data.get('user_id'):
            client = db.collection('users').document(appointment_data['user_id']).get()
            if client.exists:
                client_data = client.to_dict()
                appointment_data['client_name'] = client_data.get('name')
                appointment_data['client_email'] = client_data.get('email')
                appointment_data['client_phone'] = client_data.get('phone')
                
        appointments.append(appointment_data)
    
    return jsonify(appointments)

@app.route('/api/update-appointment-status/<appointment_id>', methods=['POST'])
@login_required
def update_appointment_status(appointment_id):
    data = request.get_json()
    status = data.get('status')
    note = data.get('note', '')
    
    if not status:
        return jsonify({'error': 'Status is required'}), 400
    
    try:
        # Get appointment
        appointment_ref = db.collection('appointments').document(appointment_id)
        appointment = appointment_ref.get()
        
        if not appointment.exists:
            return jsonify({'error': 'Appointment not found'}), 404
            
        appointment_data = appointment.to_dict()
        
        # Check if the business belongs to current user
        business_id = appointment_data.get('provider_id')
        if business_id:
            business = db.collection('providers').document(business_id).get()
            if business.exists:
                business_data = business.to_dict()
                if business_data.get('owner_id') != current_user.id:
                    return jsonify({'error': 'Unauthorized'}), 403
            else:
                return jsonify({'error': 'Provider not found'}), 404
        else:
            return jsonify({'error': 'Provider not associated with this appointment'}), 400
        
        # Create status update with current timestamp instead of SERVER_TIMESTAMP
        current_time = datetime.now()
        status_update = {
            'status': status,
            'timestamp': current_time,
        }
        
        if note:
            status_update['note'] = note
            
        # Build the update data
        update_data = {
            'status': status,
            'updated_at': firestore.SERVER_TIMESTAMP  # This is ok for a direct field update
        }
        
        # Add to status history
        if 'status_updates' not in appointment_data:
            update_data['status_updates'] = [status_update]
        else:
            update_data['status_updates'] = appointment_data['status_updates'] + [status_update]
        
        # Update the document
        appointment_ref.update(update_data)
        
        # IMPORTANT ADDITION: Record loyalty visit when appointment is marked as "completed"
        if status == 'completed':
            user_id = appointment_data.get('user_id')
            if user_id and business_id:
                # Check if business has loyalty program enabled
                if business_data.get('loyalty_enabled', False):
                    # Record a loyalty visit
                    loyalty_ref = db.collection('loyalty').document(f"{user_id}_{business_id}")
                    loyalty_doc = loyalty_ref.get()
                    
                    if not loyalty_doc.exists:
                        # Create new loyalty document
                        loyalty_data = {
                            'user_id': user_id,
                            'business_id': business_id,
                            'visits': 1,
                            'rewards_redeemed': 0,
                            'last_visit': firestore.SERVER_TIMESTAMP,
                            'created_at': firestore.SERVER_TIMESTAMP
                        }
                        loyalty_ref.set(loyalty_data)
                    else:
                        # Update existing document
                        loyalty_ref.update({
                            'visits': firestore.Increment(1),
                            'last_visit': firestore.SERVER_TIMESTAMP
                        })
                    
                    # Record visit in history
                    db.collection('loyalty_visits').add({
                        'user_id': user_id,
                        'business_id': business_id,
                        'appointment_id': appointment_id,
                        'recorded_by': current_user.id,
                        'timestamp': firestore.SERVER_TIMESTAMP
                    })
        
        # If user has email, send notification
        if appointment_data.get('user_id'):
            user_ref = db.collection('users').document(appointment_data['user_id'])
            user = user_ref.get()
            if user.exists:
                user_data = user.to_dict()
                if user_data.get('email'):
                    # Here you would implement email notification
                    # For now we're just logging it
                    print(f"Would send email to {user_data['email']} about appointment status change to {status}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error updating appointment status: {e}")
        return jsonify({'error': 'An error occurred while updating the appointment'}), 500

@app.route('/api/submit-review', methods=['POST'])
@login_required
def submit_review():
    """API endpoint to submit a review for a provider"""
    try:
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract request data
        provider_id = data.get('provider_id')
        rating = data.get('rating')
        review_text = data.get('review_text', '')
        
        # Validate required fields
        if not provider_id or not rating:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # Get Firestore client
        db = firestore.client()
        
        # Check if provider exists
        provider_ref = db.collection('providers').document(provider_id)
        provider_doc = provider_ref.get()
        
        if not provider_doc.exists:
            return jsonify({'error': 'Provider not found'}), 404
        
        # Check if user already reviewed this provider
        existing_reviews = list(db.collection('reviews')
                               .where('user_id', '==', current_user.id)
                               .where('provider_id', '==', provider_id)
                               .limit(1)
                               .stream())
        
        # Allow users to leave multiple reviews for testing purposes
        # If in production, uncomment this check:
        # if existing_reviews:
        #     return jsonify({'error': 'You have already reviewed this provider'}), 400
        
        # Create new review
        new_review = {
            'user_id': current_user.id,
            'user_name': getattr(current_user, 'display_name', current_user.email.split('@')[0]),
            'provider_id': provider_id,
            'rating': rating,
            'text': review_text,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        # Add review to Firestore
        review_ref = db.collection('reviews').document()
        review_ref.set(new_review)
        
        # Update provider's average rating
        provider_data = provider_doc.to_dict()
        current_rating = provider_data.get('average_rating', 0)
        current_count = provider_data.get('review_count', 0)
        
        # Calculate new average
        new_count = current_count + 1
        if current_count == 0:
            new_average = rating
        else:
            new_average = ((current_rating * current_count) + rating) / new_count
        
        # Update provider document
        provider_ref.update({
            'average_rating': new_average,
            'review_count': new_count
        })
        
        return jsonify({
            'success': True,
            'message': 'Review submitted successfully',
            'review_id': review_ref.id
        })
        
    except Exception as e:
        app.logger.error(f"Error submitting review: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/provider-ratings/<provider_id>')
@login_required
def get_provider_ratings(provider_id):
    """Get the rating summary for a provider"""
    try:
        # Check if provider exists
        provider_ref = db.collection('providers').document(provider_id)
        provider = provider_ref.get()
        
        if not provider.exists:
            return jsonify({'error': 'Provider not found'}), 404
            
        provider_data = provider.to_dict()
        
        # Get ratings data
        average_rating = provider_data.get('average_rating', 0)
        review_count = provider_data.get('review_count', 0)
        
        return jsonify({
            'provider_id': provider_id,
            'average_rating': average_rating,
            'review_count': review_count
        })
    except Exception as e:
        app.logger.error(f"Error getting provider ratings: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching ratings'}), 500

@app.route('/api/provider-reviews/<provider_id>')
@login_required
def get_provider_reviews(provider_id):
    """Get all reviews for a provider"""
    try:
        # Check if provider exists
        provider_ref = db.collection('providers').document(provider_id)
        if not provider_ref.get().exists:
            return jsonify({'error': 'Provider not found'}), 404
        
        # Get reviews from the reviews collection
        reviews_query = db.collection('reviews').where('provider_id', '==', provider_id).stream()
        
        reviews = []
        for review in reviews_query:
            review_data = review.to_dict()
            review_data['id'] = review.id
            
            # Format timestamp if needed
            if 'created_at' in review_data and hasattr(review_data['created_at'], 'seconds'):
                # Convert Firestore timestamp to ISO format string
                review_data['created_at'] = {
                    'seconds': review_data['created_at'].seconds,
                    'nanoseconds': review_data['created_at'].nanoseconds
                }
            
            reviews.append(review_data)
        return jsonify(reviews)
    except Exception as e:
        app.logger.error(f"Error getting provider reviews: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching reviews'}), 500

@app.route('/api/loyalty-settings/<business_id>')
@login_required
def get_loyalty_settings(business_id):
    """Get loyalty program settings for a business"""
    try:
        # Get Firestore client
        db = firestore.client()
        
        # Check if business exists and user is authorized
        business_ref = db.collection('providers').document(business_id)
        business_doc = business_ref.get()
        
        if not business_doc.exists:
            return jsonify({'error': 'Business not found'}), 404
            
        business_data = business_doc.to_dict()
        
        # If user is not the owner, they can only view if loyalty program is active
        if business_data.get('owner_id') != current_user.id:
            # Return only public settings
            loyalty_settings = {
                'enabled': business_data.get('loyalty_enabled', False),
                'visits_required': business_data.get('loyalty_visits_required', 0),
                'reward_description': business_data.get('loyalty_reward', '')
            }
            return jsonify(loyalty_settings)
        
        # Owner gets full settings
        loyalty_settings = {
            'enabled': business_data.get('loyalty_enabled', False),
            'visits_required': business_data.get('loyalty_visits_required', 10), 
            'reward_description': business_data.get('loyalty_reward', ''),
            'custom_message': business_data.get('loyalty_message', '')
        }
        
        return jsonify(loyalty_settings)
        
    except Exception as e:
        app.logger.error(f"Error fetching loyalty settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/loyalty-settings/<business_id>', methods=['POST'])
@login_required
def update_loyalty_settings(business_id):
    """Update loyalty program settings for a business"""
    try:
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Get Firestore client
        db = firestore.client()
        
        # Check if business exists and user is authorized
        business_ref = db.collection('providers').document(business_id)
        business_doc = business_ref.get()
        
        if not business_doc.exists:
            return jsonify({'error': 'Business not found'}), 404
            
        business_data = business_doc.to_dict()
        
        # Verify user is the owner
        if business_data.get('owner_id') != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403
            
        # Update loyalty settings
        update_data = {
            'loyalty_enabled': data.get('enabled', False),
            'loyalty_visits_required': data.get('visits_required', 10),
            'loyalty_reward': data.get('reward_description', ''),
            'loyalty_message': data.get('custom_message', '')
        }
        
        business_ref.update(update_data)
        
        return jsonify({
            'success': True,
            'message': 'Loyalty program settings updated successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error updating loyalty settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-loyalty/<business_id>')
@login_required
def get_user_loyalty(business_id):
    """Get user's loyalty status for a specific business"""
    try:
        # Get Firestore client
        db = firestore.client()
        
        # Check if business exists
        business_ref = db.collection('providers').document(business_id)
        business_doc = business_ref.get()
        
        if not business_doc.exists:
            return jsonify({'error': 'Business not found'}), 404
            
        business_data = business_doc.to_dict()
        
        # Check if loyalty program is enabled
        if not business_data.get('loyalty_enabled', False):
            return jsonify({
                'enabled': False,
                'message': 'Loyalty program is not enabled for this business'
            })
            
        # Get user's loyalty data
        loyalty_ref = db.collection('loyalty').document(f"{current_user.id}_{business_id}")
        loyalty_doc = loyalty_ref.get()
        
        if not loyalty_doc.exists:
            # Create new loyalty document for user if it doesn't exist
            loyalty_data = {
                'user_id': current_user.id,
                'business_id': business_id,
                'visits': 0,
                'rewards_redeemed': 0,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            loyalty_ref.set(loyalty_data)
        else:
            loyalty_data = loyalty_doc.to_dict()
            
        # Calculate progress and status
        visits_required = business_data.get('loyalty_visits_required', 10)
        current_visits = loyalty_data.get('visits', 0)
        rewards_redeemed = loyalty_data.get('rewards_redeemed', 0)
        
        # Check if reward is available
        reward_available = current_visits >= visits_required
        
        return jsonify({
            'enabled': True,
            'visits': current_visits,
            'visits_required': visits_required,
            'progress': (current_visits % visits_required) / visits_required * 100,
            'reward_available': reward_available,
            'rewards_redeemed': rewards_redeemed,
            'reward_description': business_data.get('loyalty_reward', ''),
            'custom_message': business_data.get('loyalty_message', '')
        })
        
    except Exception as e:
        app.logger.error(f"Error fetching user loyalty: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/record-loyalty-visit/<business_id>', methods=['POST'])
@login_required
def record_loyalty_visit(business_id):
    """Record a visit for the loyalty program"""
    try:
        # Get Firestore client
        db = firestore.client()
        
        # Check if business exists and user is authorized (for business owner)
        business_ref = db.collection('providers').document(business_id)
        business_doc = business_ref.get()
        
        if not business_doc.exists:
            return jsonify({'error': 'Business not found'}), 404
            
        business_data = business_doc.to_dict()
        
        # Check if loyalty program is enabled
        if not business_data.get('loyalty_enabled', False):
            return jsonify({'error': 'Loyalty program is not enabled for this business'}), 400
            
        # Get user ID - might be current user or specified user (if owner is recording)
        data = request.get_json()
        user_id = current_user.id
        
        # If request is from business owner, they can specify the user
        if business_data.get('owner_id') == current_user.id and data and 'user_id' in data:
            user_id = data['user_id']
            
        # Get user's loyalty document
        loyalty_ref = db.collection('loyalty').document(f"{user_id}_{business_id}")
        loyalty_doc = loyalty_ref.get()
        
        if not loyalty_doc.exists:
            # Create new loyalty document
            loyalty_data = {
                'user_id': user_id,
                'business_id': business_id,
                'visits': 1,
                'rewards_redeemed': 0,
                'last_visit': firestore.SERVER_TIMESTAMP,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            loyalty_ref.set(loyalty_data)
        else:
            # Update existing document
            loyalty_ref.update({
                'visits': firestore.Increment(1),
                'last_visit': firestore.SERVER_TIMESTAMP
            })
            
        # Record visit in history
        db.collection('loyalty_visits').add({
            'user_id': user_id,
            'business_id': business_id,
            'recorded_by': current_user.id,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # Get updated loyalty data
        updated_loyalty = loyalty_ref.get().to_dict()
        visits_required = business_data.get('loyalty_visits_required', 10)
        reward_available = updated_loyalty.get('visits', 0) >= visits_required
        
        return jsonify({
            'success': True,
            'visits': updated_loyalty.get('visits', 1),
            'reward_available': reward_available
        })
        
    except Exception as e:
        app.logger.error(f"Error recording loyalty visit: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/redeem-loyalty-reward/<business_id>', methods=['POST'])
@login_required
def redeem_loyalty_reward(business_id):
    """Redeem a loyalty reward"""
    try:
        # Get Firestore client
        db = firestore.client()
        
        # Check if business exists
        business_ref = db.collection('providers').document(business_id)
        business_doc = business_ref.get()
        
        if not business_doc.exists:
            return jsonify({'error': 'Business not found'}), 404
            
        business_data = business_doc.to_dict()
        
        # Check if loyalty program is enabled
        if not business_data.get('loyalty_enabled', False):
            return jsonify({'error': 'Loyalty program is not enabled for this business'}), 400
            
        # Get user ID - might be current user or specified user (if owner is redeeming)
        data = request.get_json()
        user_id = current_user.id
        
        # If request is from business owner, they can specify the user
        if business_data.get('owner_id') == current_user.id and data and 'user_id' in data:
            user_id = data['user_id']
            
        # Get user's loyalty document
        loyalty_ref = db.collection('loyalty').document(f"{user_id}_{business_id}")
        loyalty_doc = loyalty_ref.get()
        
        if not loyalty_doc.exists:
            return jsonify({'error': 'No loyalty record found for this user'}), 404
            
        loyalty_data = loyalty_doc.to_dict()
        visits_required = business_data.get('loyalty_visits_required', 10)
        
        # Check if user has enough visits
        if loyalty_data.get('visits', 0) < visits_required:
            return jsonify({
                'error': 'Not enough visits to redeem reward',
                'visits': loyalty_data.get('visits', 0),
                'visits_required': visits_required
            }), 400
            
        # Calculate new visits (subtract required visits)
        new_visits = loyalty_data.get('visits', 0) - visits_required
        
        # Update loyalty document
        loyalty_ref.update({
            'visits': new_visits,
            'rewards_redeemed': firestore.Increment(1),
            'last_redemption': firestore.SERVER_TIMESTAMP
        })
        
        # Record redemption in history
        db.collection('loyalty_redemptions').add({
            'user_id': user_id,
            'business_id': business_id,
            'recorded_by': current_user.id,
            'reward': business_data.get('loyalty_reward', ''),
            'visits_required': visits_required,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            'success': True,
            'message': 'Reward redeemed successfully',
            'remaining_visits': new_visits,
            'reward': business_data.get('loyalty_reward', '')
        })
        
    except Exception as e:
        app.logger.error(f"Error redeeming loyalty reward: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/my-loyalty')
@login_required
def my_loyalty():
    """Show user's loyalty programs and progress"""
    try:
        # Add debugging statements
        app.logger.info(f"Starting my_loyalty view for user: {current_user.id}")
        
        # Check for appointments that should be loyalty eligible
        appointments = list(db.collection('appointments')
                           .where('user_id', '==', current_user.id)
                           .where('status', '==', 'completed')
                           .stream())
        
        app.logger.info(f"Found {len(appointments)} completed appointments")
        
        # Get all loyalty records for the current user
        loyalty_programs = []
        
        # Query all loyalty documents where user is the current user
        loyalty_query = db.collection('loyalty').where('user_id', '==', current_user.id).stream()
        loyalty_docs = list(loyalty_query)
        
        app.logger.info(f"Found {len(loyalty_docs)} loyalty records")
        
        for loyalty_doc in loyalty_docs:
            loyalty_data = loyalty_doc.to_dict()
            business_id = loyalty_data.get('business_id')
            
            app.logger.info(f"Processing loyalty record for business: {business_id}")
            
            # Skip if no business ID
            if not business_id:
                app.logger.info("Skipping - no business ID")
                continue
                
            # Get business details
            business_doc = db.collection('providers').document(business_id).get()
            
            if not business_doc.exists:
                app.logger.info(f"Skipping - business {business_id} does not exist")
                continue
                
            business_data = business_doc.to_dict()
            
            # Only include businesses with active loyalty programs
            if not business_data.get('loyalty_enabled', False):
                app.logger.info(f"Skipping - loyalty not enabled for business {business_id}")
                continue
            
            visits_required = business_data.get('loyalty_visits_required', 10)
            current_visits = loyalty_data.get('visits', 0)
            rewards_redeemed = loyalty_data.get('rewards_redeemed', 0)
            
            # Calculate if reward is available
            available_rewards = current_visits // visits_required
            used_rewards = rewards_redeemed
            reward_available = available_rewards > used_rewards
            
            # Calculate progress percentage for the current cycle
            current_cycle_visits = current_visits % visits_required
            if reward_available:
                progress = 100  # Already completed
            else:
                progress = (current_cycle_visits / visits_required) * 100
            
            # Create program object
            program = {
                'business_id': business_id,
                'business_name': business_data.get('name', 'Unknown Business'),
                'visits': current_visits,
                'visits_required': visits_required,
                'rewards_redeemed': rewards_redeemed,
                'reward_available': reward_available,
                'progress': progress,
                'reward_description': business_data.get('loyalty_reward', 'Reward'),
                'custom_message': business_data.get('loyalty_message', '')
            }
            
            loyalty_programs.append(program)
        
        # If no loyalty programs found, automatically import from completed appointments
        auto_import_occurred = False
        if not loyalty_programs:
            auto_import_occurred = True
            import_count = auto_import_loyalty_data()
            if import_count > 0:
                # Re-query loyalty data if we found and imported appointments
                return redirect(url_for('my_loyalty'))
            
        # Handle specific provider highlight if requested
        highlight_provider = request.args.get('provider')
        if highlight_provider:
            for program in loyalty_programs:
                if program['business_id'] == highlight_provider:
                    program['highlight'] = True
        
        return render_template('my_loyalty.html', 
                              loyalty_programs=loyalty_programs, 
                              auto_import_occurred=auto_import_occurred)
        
    except Exception as e:
        app.logger.error(f"Error fetching loyalty programs: {str(e)}")
        flash("There was an error loading your loyalty programs. Please try again later.")
        return render_template('my_loyalty.html', loyalty_programs=[], auto_import_occurred=False)


def auto_import_loyalty_data():
    """Helper function to automatically import loyalty data from completed appointments"""
    try:
        # Get all completed appointments for the current user
        appointments_query = db.collection('appointments')\
            .where('user_id', '==', current_user.id)\
            .where('status', '==', 'completed')\
            .stream()
        
        processed_count = 0
        business_visits = {}  # Track visits per business
        
        # Process each appointment
        for appt in appointments_query:
            try:
                appt_data = appt.to_dict()
                business_id = appt_data.get('provider_id')
                
                if not business_id:
                    continue
                
                # Check if business exists and has loyalty enabled
                business_doc = db.collection('providers').document(business_id).get()
                if not business_doc:  # Use .exists property instead
                    continue
                
                business_data = business_doc.to_dict()
                # Don't call the value, just check if it's True
                if not business_data.get('loyalty_enabled', False):
                    continue
                
                # Count visits per business
                if business_id not in business_visits:
                    business_visits[business_id] = {
                        'visits': 1,
                        'business_data': business_data,
                        'last_visit': appt_data.get('updated_at', firestore.SERVER_TIMESTAMP)
                    }
                else:
                    business_visits[business_id]['visits'] += 1
                    
                    # Update last visit time if newer
                    current_last = business_visits[business_id]['last_visit']
                    appt_time = appt_data.get('updated_at')
                    if appt_time and (not current_last or appt_time > current_last):
                        business_visits[business_id]['last_visit'] = appt_time
                
                processed_count += 1
                
            except Exception as e:
                app.logger.error(f"Error processing appointment {appt.id}: {str(e)}")
        
        # Now create loyalty records for each business
        for business_id, data in business_visits.items():
            loyalty_ref = db.collection('loyalty').document(f"{current_user.id}_{business_id}")
            
            loyalty_data = {
                'user_id': current_user.id,
                'business_id': business_id,
                'visits': data['visits'],
                'rewards_redeemed': 0,
                'last_visit': data['last_visit'],
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            loyalty_ref.set(loyalty_data)
        
        if processed_count > 0:
            flash(f"We found {processed_count} completed appointments and added them to your loyalty programs!")
            
        return processed_count
        
    except Exception as e:
        app.logger.error(f"Error in auto loyalty import: {str(e)}")
        flash("There was an error importing your loyalty data.")
        return 0

# Add this route after the my_loyalty function
@app.route('/migrate-loyalty-data')
@login_required
def migrate_loyalty_data():
    """
    Migration helper to populate loyalty data from completed appointments.
    This should only be run once when setting up the loyalty system.
    """
    try:
        # Get all completed appointments for the current user
        appointments_query = db.collection('appointments')\
            .where('user_id', '==', current_user.id)\
            .where('status', '==', 'completed')\
            .stream()
        
        # Track which appointments have already been processed for loyalty
        processed_appointments = set()
        
        # First, get all existing loyalty visit records to avoid duplicates
        existing_visits = db.collection('loyalty_visits')\
            .where('user_id', '==', current_user.id)\
            .stream()
            
        # Create a set of appointment IDs that have already been processed
        for visit in existing_visits:
            visit_data = visit.to_dict()
            if 'appointment_id' in visit_data:
                processed_appointments.add(visit_data['appointment_id'])
                
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        # Track visits per business to avoid duplicate counting
        business_visits = {}
        
        # Process each appointment
        for appt in appointments_query:
            try:
                # Skip if this appointment has already been processed for loyalty
                if appt.id in processed_appointments:
                    skipped_count += 1
                    continue
                    
                appt_data = appt.to_dict()
                business_id = appt_data.get('provider_id')
                
                if not business_id:
                    skipped_count += 1
                    continue
                
                # Check if business exists and has loyalty enabled
                business_doc = db.collection('providers').document(business_id).get()
                if not business_doc.exists:
                    skipped_count += 1
                    continue
                
                business_data = business_doc.to_dict()
                if not business_data.get('loyalty_enabled', False):
                    skipped_count += 1
                    continue
                
                # Add to business visits counter
                if business_id not in business_visits:
                    business_visits[business_id] = {
                        'count': 0,
                        'last_visit': None
                    }
                
                business_visits[business_id]['count'] += 1
                
                # Track last visit time
                visit_time = appt_data.get('updated_at', firestore.SERVER_TIMESTAMP)
                if not business_visits[business_id]['last_visit'] or \
                   (visit_time and business_visits[business_id]['last_visit'] < visit_time):
                    business_visits[business_id]['last_visit'] = visit_time
                
                # Record this visit in the loyalty_visits collection to prevent future duplicate processing
                db.collection('loyalty_visits').add({
                    'user_id': current_user.id,
                    'business_id': business_id,
                    'appointment_id': appt.id,
                    'recorded_by': current_user.id,
                    'timestamp': firestore.SERVER_TIMESTAMP,
                    'visit_date': visit_time,
                    'migrated': True
                })
                
                # Record was successfully processed
                processed_count += 1
                
            except Exception as e:
                app.logger.error(f"Error processing appointment {appt.id}: {str(e)}")
                error_count += 1
        
        # Now update loyalty documents with aggregated visit counts
        for business_id, visit_data in business_visits.items():
            # Get or create loyalty document
            loyalty_ref = db.collection('loyalty').document(f"{current_user.id}_{business_id}")
            loyalty_doc = loyalty_ref.get()
            
            if not loyalty_doc.exists:
                # Create new loyalty document
                loyalty_data = {
                    'user_id': current_user.id,
                    'business_id': business_id,
                    'visits': visit_data['count'],
                    'rewards_redeemed': 0,
                    'last_visit': visit_data['last_visit'],
                    'created_at': firestore.SERVER_TIMESTAMP
                }
                loyalty_ref.set(loyalty_data)
            else:
                # Update existing document - increment by the newly processed visits
                # We're not using Increment here because we want to add the exact number of new visits
                loyalty_data = loyalty_doc.to_dict()
                existing_visits = loyalty_data.get('visits', 0)
                
                loyalty_ref.update({
                    'visits': existing_visits + visit_data['count'],
                    'last_visit': visit_data['last_visit'] or firestore.SERVER_TIMESTAMP
                })
        
        flash(f"Migration complete: {processed_count} appointments processed, {skipped_count} skipped, {error_count} errors")
        return redirect(url_for('my_loyalty'))
    
    except Exception as e:
        app.logger.error(f"Error in loyalty migration: {str(e)}")
        flash("There was an error migrating loyalty data. Please try again later.")
        return redirect(url_for('my_loyalty'))

@app.route('/redeem-reward/<business_id>')
@login_required
def redeem_reward(business_id):
    """Allow user to redeem a loyalty reward"""
    try:
        # Check if business exists
        business_doc = db.collection('providers').document(business_id).get()
        
        if not business_doc.exists:
            flash('Business not found')
            return redirect(url_for('my_loyalty'))
            
        business_data = business_doc.to_dict()
        
        # Check if loyalty program is enabled
        if not business_data.get('loyalty_enabled', False):
            flash('This business does not have an active loyalty program')
            return redirect(url_for('my_loyalty'))
            
        # Get user's loyalty document
        loyalty_ref = db.collection('loyalty').document(f"{current_user.id}_{business_id}")
        loyalty_doc = loyalty_ref.get()
        
        if not loyalty_doc.exists:
            flash('You do not have a loyalty record with this business')
            return redirect(url_for('my_loyalty'))
            
        loyalty_data = loyalty_doc.to_dict()
        visits_required = business_data.get('loyalty_visits_required', 10)
        
        # Calculate if reward is available
        current_visits = loyalty_data.get('visits', 0)
        rewards_redeemed = loyalty_data.get('rewards_redeemed', 0)
        
        available_rewards = current_visits // visits_required
        used_rewards = rewards_redeemed
        
        if available_rewards <= used_rewards:
            flash('You do not have any rewards available to redeem')
            return redirect(url_for('my_loyalty'))
        
        # Instead of calling the API directly, let's implement the redemption logic here
        try:
            # Calculate new visits (current visits are enough for one more reward)
            new_visits = current_visits - visits_required
            
            # Generate a unique redemption code
            redemption_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Save redemption in history with the code
            redemption_ref = db.collection('loyalty_redemptions').add({
                'user_id': current_user.id,
                'user_email': current_user.email,
                'user_name': getattr(current_user, 'name', current_user.email.split('@')[0]),
                'business_id': business_id,
                'business_name': business_data.get('name', 'Unknown Business'),
                'recorded_by': current_user.id,
                'reward': business_data.get('loyalty_reward', ''),
                'code': redemption_code,
                'visits_required': visits_required,
                'status': 'pending',  # Will be marked as 'redeemed' when used at business
                'created_at': firestore.SERVER_TIMESTAMP,
                'expires_at': datetime.now() + timedelta(days=30)  # Code expires in 30 days
            })
            
            # Update loyalty document
            loyalty_ref.update({
                'visits': new_visits,
                'rewards_redeemed': firestore.Increment(1),
                'last_redemption': firestore.SERVER_TIMESTAMP
            })
            
            # Send notification to business owner
            owner_id = business_data.get('owner_id')
            if owner_id:
                # Create notification document
                db.collection('notifications').add({
                    'recipient_id': owner_id,
                    'type': 'loyalty_redemption',
                    'title': 'Loyalty Reward Redeemed',
                    'message': f"{current_user.name or current_user.email} has redeemed a loyalty reward: {business_data.get('loyalty_reward', 'Reward')}",
                    'business_id': business_id,
                    'user_id': current_user.id,
                    'code': redemption_code,
                    'read': False,
                    'created_at': firestore.SERVER_TIMESTAMP
                })
                
                # Get owner's email for potential email notification
                owner_doc = db.collection('users').document(owner_id).get()
                if owner_doc.exists:
                    owner_data = owner_doc.to_dict()
                    owner_email = owner_data.get('email')
                    
                    # For future implementation: Send email to business owner
                    # This would require setting up an email service
                    print(f"Would send email to {owner_email} about loyalty redemption code {redemption_code}")
            
            # Show confirmation page with redemption code
            return render_template('redeem_rewards.html',
                                  business=business_data,
                                  reward=business_data.get('loyalty_reward', 'Reward'),
                                  redemption_code=redemption_code,
                                  expiration=datetime.now() + timedelta(days=30))
                                  
        except Exception as e:
            app.logger.error(f"Error during reward redemption: {str(e)}")
            flash(f"Error redeeming reward: {str(e)}")
            return redirect(url_for('my_loyalty'))
        
    except Exception as e:
        app.logger.error(f"Error redeeming reward: {str(e)}")
        flash("There was an error processing your redemption. Please try again later.")
        return redirect(url_for('my_loyalty'))
    

@app.route('/api/verify-reward-code', methods=['POST'])
@login_required
def verify_reward_code():
    """Verify a loyalty reward redemption code"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'valid': False, 'error': 'No data provided'}), 400
            
        code = data.get('code')
        business_id = data.get('business_id')
        
        if not code or not business_id:
            return jsonify({'valid': False, 'error': 'Missing code or business ID'}), 400
            
        # Check if business belongs to current user
        business_doc = db.collection('providers').document(business_id).get()
        if not business_doc.exists:
            return jsonify({'valid': False, 'error': 'Business not found'}), 404
            
        business_data = business_doc.to_dict()
        if business_data.get('owner_id') != current_user.id:
            return jsonify({'valid': False, 'error': 'Unauthorized'}), 403
            
        # Query for the redemption code
        redemptions = db.collection('loyalty_redemptions')\
            .where('code', '==', code)\
            .stream()
            
        # Filter manually for business ID since multiple where clauses are causing issues
        redemption_doc = None
        for doc in redemptions:
            doc_data = doc.to_dict()
            if doc_data.get('business_id') == business_id:
                redemption_doc = doc
                redemption_data = doc_data
                break
        
        if not redemption_doc:
            return jsonify({'valid': False, 'error': 'Redemption code not found'}), 404
            
        # Check if code is expired
        if 'expires_at' in redemption_data:
            expires_at = redemption_data['expires_at']
            # Convert to naive datetime object for comparison if it's timezone-aware
            if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is not None:
                # Convert to UTC then remove timezone info
                expires_at = expires_at.astimezone(timezone.utc).replace(tzinfo=None)
            
            # Make sure current time is naive for comparison
            current_time = datetime.now()
            if current_time > expires_at:
                return jsonify({'valid': False, 'error': 'This code has expired'}), 400
                
        # Check if already redeemed
        if redemption_data.get('status') == 'redeemed':
            return jsonify({'valid': False, 'error': 'This code has already been redeemed'}), 400
            
        # Return validation result with user info
        return jsonify({
            'valid': True,
            'user_id': redemption_data.get('user_id'),
            'user_email': redemption_data.get('user_email'),
            'user_name': redemption_data.get('user_name', ''),
            'reward': redemption_data.get('reward', ''),
            'created_at': str(redemption_data.get('created_at')),
            'code': code
        })
        
    except Exception as e:
        app.logger.error(f"Error verifying reward code: {str(e)}")
        return jsonify({'valid': False, 'error': str(e)}), 500

@app.route('/api/mark-reward-redeemed', methods=['POST'])
@login_required
def mark_reward_redeemed():
    """Mark a loyalty reward as redeemed"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        code = data.get('code')
        business_id = data.get('business_id')
        
        if not code or not business_id:
            return jsonify({'success': False, 'error': 'Missing code or business ID'}), 400
            
        # Check if business belongs to current user
        business_doc = db.collection('providers').document(business_id).get()
        if not business_doc.exists:
            return jsonify({'success': False, 'error': 'Business not found'}), 404
            
        business_data = business_doc.to_dict()
        if business_data.get('owner_id') != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
        # Query for the redemption code
        redemptions = db.collection('loyalty_redemptions')\
            .where('code', '==', code)\
            .stream()
            
        # Filter manually for business ID
        redemption_doc = None
        for doc in redemptions:
            doc_data = doc.to_dict()
            if doc_data.get('business_id') == business_id:
                redemption_doc = doc
                redemption_data = doc_data
                break
        
        if not redemption_doc:
            return jsonify({'success': False, 'error': 'Redemption code not found'}), 404
            
        # Check if code is expired
        if 'expires_at' in redemption_data:
            expires_at = redemption_data['expires_at']
            # Convert to naive datetime object for comparison if it's timezone-aware
            if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is not None:
                # Convert to UTC then remove timezone info
                expires_at = expires_at.astimezone(timezone.utc).replace(tzinfo=None)
            
            # Make sure current time is naive for comparison
            current_time = datetime.now()
            if current_time > expires_at:
                return jsonify({'success': False, 'error': 'This code has expired'}), 400
                
        # Check if already redeemed
        if redemption_data.get('status') == 'redeemed':
            return jsonify({'success': False, 'error': 'This code has already been redeemed'}), 400
            
        # Mark as redeemed
        db.collection('loyalty_redemptions').document(redemption_doc.id).update({
            'status': 'redeemed',
            'redeemed_at': firestore.SERVER_TIMESTAMP,
            'redeemed_by': current_user.id
        })
        
        # Add notification for the user
        db.collection('notifications').add({
            'recipient_id': redemption_data.get('user_id'),
            'type': 'reward_redeemed',
            'title': 'Reward Redeemed',
            'message': f"Your reward at {business_data.get('name')} has been redeemed.",
            'business_id': business_id,
            'read': False,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            'success': True, 
            'message': 'Reward successfully marked as redeemed'
        })
        
    except Exception as e:
        app.logger.error(f"Error marking reward as redeemed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/cleanup-database', methods=['GET', 'POST'])
@login_required
def cleanup_database():
    """Admin function to clean up database collections"""
    # Check if user is admin - IMPORTANT FOR SECURITY!
    # Replace this with your actual admin check logic
    user_doc = db.collection('users').document(current_user.id).get()
    if not user_doc.exists or current_user.email != 'admin@example.com':
        flash('Unauthorized: Admin access required')
        return redirect(url_for('dashboard'))
    
    form = FlaskForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        collections_to_clean = request.form.getlist('collections')
        confirmation_code = request.form.get('confirmation_code')
        
        # Extra security - require a confirmation code
        if confirmation_code != "DELETE-CONFIRM":
            flash('Invalid confirmation code')
            return redirect(url_for('cleanup_database'))
        
        # Batch size for deletion (Firestore has limits)
        batch_size = 500
        total_deleted = 0
        
        for collection_name in collections_to_clean:
            try:
                deleted = delete_collection(db, collection_name, batch_size)
                total_deleted += deleted
                flash(f"Deleted {deleted} documents from {collection_name}")
            except Exception as e:
                flash(f"Error deleting from {collection_name}: {str(e)}")
        
        flash(f"Database cleanup completed. Total documents deleted: {total_deleted}")
    
    # Get list of collections for the form
    collections = [
        'appointments',
        'health_data',
        'loyalty',
        'loyalty_redemptions',
        'loyalty_visits',
        'notifications',
        'providers',
        'reviews',
        # Don't include 'users' by default as it's risky to delete user accounts
    ]
    
    return render_template('admin/cleanup_database.html', form=form, collections=collections)

def delete_collection(db, collection_name, batch_size):
    """Helper function to delete all documents in a collection"""
    deleted_count = 0
    docs = db.collection(collection_name).limit(batch_size).stream()
    docs_list = list(docs)
    
    if not docs_list:
        return 0
    
    for doc in docs_list:
        doc.reference.delete()
        deleted_count += 1
    
    # If we've deleted a full batch, there might be more
    if len(docs_list) >= batch_size:
        # Recursively delete more
        deleted_count += delete_collection(db, collection_name, batch_size)
    
    return deleted_count

def delete_collection_documents(db, collection_name, batch_size):
    """Helper function to delete all documents in a collection without removing the collection itself"""
    deleted_count = 0
    docs = db.collection(collection_name).limit(batch_size).stream()
    docs_list = list(docs)
    
    if not docs_list:
        return 0
    
    for doc in docs_list:
        doc.reference.delete()
        deleted_count += 1
    
    # If we've deleted a full batch, there might be more
    if len(docs_list) >= batch_size:
        # Recursively delete more
        deleted_count += delete_collection_documents(db, collection_name, batch_size)
    
    return deleted_count

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    """Admin dashboard for system management"""
    # Check if user is admin - only allow specific admin emails
    authorized_admins = ['root@gmail.com']  # Add your admin email
    if current_user.email not in authorized_admins:
        flash('Unauthorized: Admin access required')
        return redirect(url_for('dashboard'))
    
    # Create form for CSRF protection
    form = FlaskForm()
    
    # Get all providers for the admin panel
    providers = []
    providers_query = db.collection('providers').stream()
    for doc in providers_query:
        provider_data = doc.to_dict()
        provider_data['id'] = doc.id
        providers.append(provider_data)
    
    # Handle database cleanup request
    if request.method == 'POST' and form.validate_on_submit():
        collections_to_clean = request.form.getlist('collections')
        confirmation_code = request.form.get('confirmation_code')
        
        # Extra security - require a confirmation code
        if confirmation_code != "DELETE-CONFIRM":
            flash('Invalid confirmation code')
            return redirect(url_for('admin_dashboard'))
        
        # Batch size for deletion (Firestore has limits)
        batch_size = 500
        total_deleted = 0
        
        for collection_name in collections_to_clean:
            try:
                # Use the new function that preserves collections but removes documents
                deleted = delete_collection_documents(db, collection_name, batch_size)
                total_deleted += deleted
                flash(f"Cleared {deleted} documents from {collection_name}")
            except Exception as e:
                flash(f"Error clearing documents from {collection_name}: {str(e)}")
        
        flash(f"Database cleanup completed. Total documents deleted: {total_deleted}")
        return redirect(url_for('admin_dashboard'))
    
    # Get list of collections for the form
    collections = [
        'appointments',
        'health_data',
        'loyalty',
        'loyalty_redemptions',
        'loyalty_visits',
        'notifications',
        'providers',
        'reviews',
        # Don't include 'users' by default as it's risky to delete user accounts
    ]
    
    return render_template('admin.html', form=form, collections=collections, providers=providers)

if __name__ == '__main__':
    app.run(debug=False)