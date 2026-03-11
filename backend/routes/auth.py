"""Authentication routes - Login, Register, JWT token management."""
import jwt
import datetime
from flask import Blueprint, request, jsonify, current_app, g
from models import db, User, Company, Student
from utils.decorators import token_required

auth_bp = Blueprint('auth', __name__)


def generate_token(user):
    """Generate a JWT token for a user."""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(
            seconds=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)
        )
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')


@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new student or company."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', '').strip().lower()

    # Validation
    if not email or not password or not role:
        return jsonify({'error': 'Email, password and role are required'}), 400

    if role not in ['student', 'company']:
        return jsonify({'error': 'Invalid role. Must be student or company'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists'}), 409

    try:
        # Create user
        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get the user ID

        if role == 'student':
            name = data.get('name', '').strip()
            if not name:
                return jsonify({'error': 'Name is required for student registration'}), 400

            student = Student(
                user_id=user.id,
                name=name,
                roll_number=data.get('roll_number', '').strip(),
                phone=data.get('phone', '').strip(),
                branch=data.get('branch', '').strip(),
                cgpa=float(data.get('cgpa', 0)) if data.get('cgpa') else None,
                year=int(data.get('year', 0)) if data.get('year') else None,
                skills=data.get('skills', '').strip()
            )
            db.session.add(student)

        elif role == 'company':
            name = data.get('company_name', '').strip()
            if not name:
                return jsonify({'error': 'Company name is required'}), 400

            company = Company(
                user_id=user.id,
                name=name,
                industry=data.get('industry', '').strip(),
                location=data.get('location', '').strip(),
                website=data.get('website', '').strip(),
                hr_name=data.get('hr_name', '').strip(),
                hr_email=data.get('hr_email', email).strip(),
                hr_phone=data.get('hr_phone', '').strip(),
                description=data.get('description', '').strip(),
                company_size=data.get('company_size', '').strip(),
                approval_status='pending'
            )
            db.session.add(company)

        db.session.commit()

        token = generate_token(user)

        return jsonify({
            'message': f'{"Student" if role == "student" else "Company"} registered successfully' +
                       (' (pending admin approval)' if role == 'company' else ''),
            'token': token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Log in a user and return a JWT token."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Your account has been deactivated. Please contact admin.'}), 403

    # Check if company is blacklisted
    if user.role == 'company' and user.company:
        if user.company.is_blacklisted:
            return jsonify({'error': 'Your company has been blacklisted. Please contact admin.'}), 403

    # Check if student is blacklisted
    if user.role == 'student' and user.student:
        if user.student.is_blacklisted:
            return jsonify({'error': 'Your account has been blacklisted. Please contact admin.'}), 403

    # Update last login
    user.last_login = datetime.datetime.utcnow()
    db.session.commit()

    token = generate_token(user)

    # Build response with profile data
    response_data = {
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }

    if user.role == 'company' and user.company:
        response_data['company'] = user.company.to_dict()
    elif user.role == 'student' and user.student:
        response_data['student'] = user.student.to_dict()

    return jsonify(response_data), 200


@auth_bp.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current authenticated user profile."""
    user = g.current_user

    response_data = {'user': user.to_dict()}

    if user.role == 'company' and user.company:
        response_data['company'] = user.company.to_dict()
    elif user.role == 'student' and user.student:
        response_data['student'] = user.student.to_dict()

    return jsonify(response_data), 200


@auth_bp.route('/api/auth/change-password', methods=['PUT'])
@token_required
def change_password():
    """Change user password."""
    data = request.get_json()
    user = g.current_user

    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({'error': 'Both old and new passwords are required'}), 400

    if not user.check_password(old_password):
        return jsonify({'error': 'Current password is incorrect'}), 401

    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400

    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'}), 200
