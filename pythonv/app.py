from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(50))
    appointments = db.relationship('Appointment', backref='user', lazy=True)
    health_data = db.relationship('HealthData', backref='user', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    cost = db.Column(db.Float)

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    steps = db.Column(db.Integer, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=False)

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    languages = db.Column(db.String(200))
    cultural_background = db.Column(db.String(100))
    lgbtq_friendly = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        language = request.form.get('language')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists')
        else:
            new_user = User(email=email, password=generate_password_hash(password), name=name, language=language)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.date).limit(5).all()
    health_data = HealthData.query.filter_by(user_id=current_user.id).order_by(HealthData.date.desc()).first()
    return render_template('dashboard.html', appointments=appointments, health_data=health_data)

@app.route('/appointments')
@login_required
def appointments():
    appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.date).all()
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
        
        new_appointment = Appointment(user_id=current_user.id, doctor_name=doctor_name, type=appointment_type, date=date, cost=cost)
        db.session.add(new_appointment)
        db.session.commit()
        flash('Appointment booked successfully!')
        return redirect(url_for('appointments'))
    
    providers = Provider.query.all()
    return render_template('book_appointment.html', providers=providers)

@app.route('/health_tracker')
@login_required
def health_tracker():
    health_data = HealthData.query.filter_by(user_id=current_user.id).order_by(HealthData.date.desc()).limit(7).all()
    return render_template('health_tracker.html', health_data=health_data)

@app.route('/add_health_data', methods=['POST'])
@login_required
def add_health_data():
    date = datetime.now().date()
    steps = request.form.get('steps', type=int)
    calories = request.form.get('calories', type=int)
    sleep_hours = request.form.get('sleep_hours', type=float)
    
    new_data = HealthData(user_id=current_user.id, date=date, steps=steps, calories=calories, sleep_hours=sleep_hours)
    db.session.add(new_data)
    db.session.commit()
    flash('Health data added successfully!')
    return redirect(url_for('health_tracker'))

@app.route('/api/health_data')
@login_required
def api_health_data():
    days = request.args.get('days', default=7, type=int)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    health_data = HealthData.query.filter(HealthData.user_id == current_user.id, 
                                          HealthData.date >= start_date,
                                          HealthData.date <= end_date).order_by(HealthData.date).all()
    
    data = [{
        'date': item.date.strftime('%Y-%m-%d'),
        'steps': item.steps,
        'calories': item.calories,
        'sleep_hours': item.sleep_hours
    } for item in health_data]
    
    return jsonify(data)

@app.route('/community_support')
@login_required
def community_support():
    return render_template('community_support.html')

@app.route('/telehealth')
@login_required
def telehealth():
    return render_template('telehealth.html')

@app.route('/cost_comparison')
@login_required
def cost_comparison():
    return render_template('cost_comparison.html')

@app.route('/crisis_resources')
def crisis_resources():
    return render_template('crisis_resources.html')

@app.route('/find_providers')
@login_required
def find_providers():
    return render_template('find_providers.html')

@app.route('/api/providers')
@login_required
def api_providers():
    # This is a mock implementation. In a real app, you'd query a database.
    providers = [
        {"id": 1, "name": "Dr. Smith", "specialty": "Dentist", "distance": 2.5},
        {"id": 2, "name": "Dr. Johnson", "specialty": "Optometrist", "distance": 1.8},
        {"id": 3, "name": "Dr. Williams", "specialty": "General Practitioner", "distance": 3.2},
        {"id": 4, "name": "Dr. Brown", "specialty": "Pediatrician", "distance": 4.1},
        {"id": 5, "name": "Dr. Davis", "specialty": "Dermatologist", "distance": 2.9},
    ]
    return jsonify(providers)

@app.route('/api/provider/<int:provider_id>')
@login_required
def api_provider(provider_id):
    # This is a mock implementation. In a real app, you'd query a database.
    providers = {
        1: {"id": 1, "name": "Dr. Smith", "specialty": "Dentist", "address": "123 Main St", "phone": "555-1234"},
        2: {"id": 2, "name": "Dr. Johnson", "specialty": "Optometrist", "address": "456 Elm St", "phone": "555-5678"},
        3: {"id": 3, "name": "Dr. Williams", "specialty": "General Practitioner", "address": "789 Oak St", "phone": "555-9012"},
        4: {"id": 4, "name": "Dr. Brown", "specialty": "Pediatrician", "address": "321 Pine St", "phone": "555-3456"},
        5: {"id": 5, "name": "Dr. Davis", "specialty": "Dermatologist", "address": "654 Maple St", "phone": "555-7890"},
    }
    provider = providers.get(provider_id)
    if provider:
        return jsonify(provider)
    else:
        return jsonify({"error": "Provider not found"}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

