from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template, session
from models import db, User
import jwt
import datetime
from functools import wraps
from flask import current_app
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

def generate_jwt(user):
    """
    Generates a JWT token for a user.
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': user.id,
            'role': user.role
        }
        return jwt.encode(
            payload,
            current_app.config.get('JWT_SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return str(e)

def token_required(f):
    """
    Decorator to protect API routes with JWT.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        # Fallback to session for browser requests
        if not token:
            if 'user_id' in session:
                current_user = User.query.get(session['user_id'])
                if current_user:
                    return f(current_user, *args, **kwargs)
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, current_app.config.get('JWT_SECRET_KEY'), algorithms=['HS256'])
            current_user = User.query.get(data['sub'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('views.dashboard'))
        
    if request.method == 'POST':
        # Check if form or JSON
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
        else:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
        if not username or not email or not password:
            if request.is_json:
                return jsonify({'message': 'Missing fields!'}), 400
            flash('All fields are required!', 'danger')
            return render_template('signup.html')
            
        # Check if user exists
        if User.query.filter((User.username == username) | (User.email == email)).first():
            if request.is_json:
                return jsonify({'message': 'Username or email already exists!'}), 400
            flash('Username or email already exists!', 'danger')
            return render_template('signup.html')
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        # If specific email, make admin for testing
        if email.lower() == 'admin@foodiefinds.ai':
            user.role = 'admin'
            
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            token = generate_jwt(user)
            return jsonify({'message': 'User registered successfully!', 'token': token, 'user': user.to_dict()}), 201
            
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('views.dashboard'))
        
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            email = request.form.get('email')
            password = request.form.get('password')
            
        if not email or not password:
            if request.is_json:
                return jsonify({'message': 'Missing fields!'}), 400
            flash('Please enter both email and password!', 'warning')
            return render_template('login.html')
            
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Store in session for browser
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            if request.is_json:
                token = generate_jwt(user)
                return jsonify({'message': 'Login successful!', 'token': token, 'user': user.to_dict()}), 200
                
            flash(f'Welcome back, {user.username}!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('views.dashboard'))
        else:
            if request.is_json:
                return jsonify({'message': 'Invalid credentials!'}), 401
            flash('Invalid email or password!', 'danger')
            return render_template('login.html')
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('views.landing'))

@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    """
    Simulated Google Sign-In endpoint.
    Expects google credential info in JSON request, then logs in/registers.
    """
    data = request.get_json() or {}
    email = data.get('email')
    name = data.get('name')
    google_id = data.get('google_id')
    
    if not email or not name:
        return jsonify({'message': 'Invalid Google account data!'}), 400
        
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        # Create a new user with random password
        username = email.split('@')[0]
        # Append some random digits to make unique if needed
        import random
        while User.query.filter_by(username=username).first():
            username = f"{email.split('@')[0]}_{random.randint(10, 99)}"
            
        user = User(username=username, email=email)
        user.set_password(f"google_oauth_{google_id or random.randint(1000, 9999)}")
        db.session.add(user)
        db.session.commit()
        
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    
    token = generate_jwt(user)
    return jsonify({
        'message': 'Google login successful!',
        'token': token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate a secure reset link placeholder (mock reset flow)
            # In production, this would send an email with a secure token.
            flash(f"A password reset link has been simulated for {email}. In a production environment, an email would be dispatched.", "success")
        else:
            flash("No account associated with that email address.", "danger")
        return render_template('login.html')
        
    return render_template('login.html', show_forgot_modal=True)
