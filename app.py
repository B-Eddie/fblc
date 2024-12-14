import os
from flask import Flask, render_template, request, redirect, url_for, flash
from firebase_admin import credentials, initialize_app, auth
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Used for flashing messages

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-adminsdk.json")
initialize_app(cred)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            # Create new Firebase user
            user = auth.create_user(
                email=email,
                password=password
            )
            flash('User created successfully!', 'success')
            return redirect(url_for('log_in'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('sign_up.html')

@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Authenticate the user using Firebase
            user = auth.get_user_by_email(email)
            # You can add password verification here, but Firebase Authentication manages it

            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))  # Redirect to home page after login
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return render_template('log_in.html')

if __name__ == '__main__':
    app.run(debug=True)
