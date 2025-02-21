from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')

# Initialize Firebase
cred = credentials.Certificate("fblc/pythonv/firebaseconfig.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, uid, email, name, language):
        self.id = uid
        self.email = email
        self.name = name
        self.language = language

@login_manager.user_loader
def load_user(user_id):
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return User(user_id, user_data['email'], user_data['name'], user_data['language'])
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.get_user_by_email(email)
            user_doc = db.collection('users').document(user.uid).get()
            user_data = user_doc.to_dict()
            if check_password_hash(user_data['password'], password):
                login_user(User(user.uid, email, user_data['name'], user_data['language']))
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password')
        except:
            flash('Invalid email or password')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        language = request.form.get('language')
        try:
            user = auth.create_user(email=email, password=password)
            db.collection('users').document(user.uid).set({
                'email': email,
                'password': generate_password_hash(password),
                'name': name,
                'language': language
            })
            login_user(User(user.uid, email, name, language))
            return redirect(url_for('dashboard'))
        except:
            flash('Email already exists')
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    appointments = db.collection('appointments').where('user_id', '==', current_user.id).order_by('date').limit(5).stream()
    health_data = db.collection('health_data').where('user_id', '==', current_user.id).order_by('date', direction=firestore.Query.DESCENDING).limit(1).stream()
    return render_template('dashboard.html', appointments=appointments, health_data=next(health_data, None))

@app.route('/appointments')
@login_required
def appointments():
    appointments = db.collection('appointments').where('user_id', '==', current_user.id).order_by('date').stream()
    return render_template('appointments.html', appointments=appointments)

@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
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
    
    providers = db.collection('providers').where('verified', '==', True).stream()
    return render_template('book_appointment.html', providers=providers)

@app.route('/health_tracker')
@login_required
def health_tracker():
    health_data = db.collection('health_data').where('user_id', '==', current_user.id).order_by('date', direction=firestore.Query.DESCENDING).limit(7).stream()
    return render_template('health_tracker.html', health_data=health_data)

@app.route('/add_health_data', methods=['POST'])
@login_required
def add_health_data():
    date = datetime.now().date()
    steps = request.form.get('steps', type=int)
    calories = request.form.get('calories', type=int)
    sleep_hours = request.form.get('sleep_hours', type=float)
    
    db.collection('health_data').add({
        'user_id': current_user.id,
        'date': date,
        'steps': steps,
        'calories': calories,
        'sleep_hours': sleep_hours
    })
    flash('Health data added successfully!')
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
    if request.method == 'POST':
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
    
    return render_template('add_business.html')

@app.route('/api/providers')
@login_required
def api_providers():
    providers = db.collection('providers').where('verified', '==', True).stream()
    provider_list = [{
        'id': doc.id,
        'name': doc.to_dict()['name'],
        'specialty': doc.to_dict()['specialty'],
        'distance': 0  # You would calculate this based on user's location
    } for doc in providers]
    return jsonify(provider_list)

@app.route('/api/provider/<provider_id>')
@login_required
def api_provider(provider_id):
    provider = db.collection('providers').document(provider_id).get()
    if provider.exists:
        provider_data = provider.to_dict()
        return jsonify({
            'id': provider.id,
            'name': provider_data['name'],
            'specialty': provider_data['specialty'],
            'address': provider_data['address'],
            'phone': provider_data['phone']
        })
    else:
        return jsonify({"error": "Provider not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

