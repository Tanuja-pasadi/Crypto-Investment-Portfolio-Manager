from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import os

from extensions import db, login_manager
from models import User
from crypto_logic import get_dashboard_data, calculate_portfolio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-crypto-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cryptoapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
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
        else:
            flash('Invalid login credentials', 'danger')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists. Go to login page.', 'danger')
            return redirect(url_for('signup'))
            
        new_user = User(email=email, username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/api/dashboard_data')
@login_required
def api_dashboard_data():
    try:
        data = get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/calculator', methods=['GET', 'POST'])
@login_required
def calculator():
    if request.method == 'POST':
        try:
            amount_str = request.form.get('amount')
            if not amount_str:
                flash('Please enter an amount.', 'warning')
                return render_template('calculator.html', user=current_user)
                
            amount = float(amount_str)
            results = calculate_portfolio(amount)
            return render_template('calculator.html', user=current_user, results=results, amount=amount)
        except Exception as e:
            flash(f"Error calculating portfolio: {str(e)}", "danger")
            return render_template('calculator.html', user=current_user)
            
    return render_template('calculator.html', user=current_user)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_username = request.form.get('username')
        current_user.username = new_username
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
    return render_template('profile.html', user=current_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
