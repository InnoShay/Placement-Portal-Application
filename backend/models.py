from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, company, student
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    company = db.relationship('Company', backref='user', uselist=False, cascade='all, delete-orphan')
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(200))
    website = db.Column(db.String(300))
    hr_name = db.Column(db.String(100))
    hr_email = db.Column(db.String(120))
    hr_phone = db.Column(db.String(20))
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    company_size = db.Column(db.String(50))  # e.g., '1-50', '51-200', '201-500', '500+'
    founded_year = db.Column(db.Integer)
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job_positions = db.relationship('JobPosition', backref='company', lazy='dynamic', cascade='all, delete-orphan')
    placements = db.relationship('Placement', backref='company', lazy='dynamic')

    def to_dict(self, include_jobs=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'industry': self.industry,
            'location': self.location,
            'website': self.website,
            'hr_name': self.hr_name,
            'hr_email': self.hr_email,
            'hr_phone': self.hr_phone,
            'description': self.description,
            'logo_url': self.logo_url,
            'company_size': self.company_size,
            'founded_year': self.founded_year,
            'approval_status': self.approval_status,
            'is_blacklisted': self.is_blacklisted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_jobs': self.job_positions.count() if self.job_positions else 0
        }
        if include_jobs:
            data['jobs'] = [job.to_dict() for job in self.job_positions.all()]
        return data


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(20))
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    year = db.Column(db.Integer)  # graduation year
    skills = db.Column(db.Text)  # comma-separated or JSON
    bio = db.Column(db.Text)
    resume_path = db.Column(db.String(500))
    linkedin_url = db.Column(db.String(300))
    github_url = db.Column(db.String(300))
    experience = db.Column(db.Text)  # JSON string of experience entries
    education = db.Column(db.Text)   # JSON string of education entries
    is_blacklisted = db.Column(db.Boolean, default=False)
    is_placed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    placements = db.relationship('Placement', backref='student', lazy='dynamic')

    def to_dict(self, include_applications=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'roll_number': self.roll_number,
            'email': self.user.email if self.user else None,
            'phone': self.phone,
            'branch': self.branch,
            'cgpa': self.cgpa,
            'year': self.year,
            'skills': self.skills,
            'bio': self.bio,
            'resume_path': self.resume_path,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'experience': self.experience,
            'education': self.education,
            'is_blacklisted': self.is_blacklisted,
            'is_placed': self.is_placed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_applications': self.applications.count() if self.applications else 0
        }
        if include_applications:
            data['applications'] = [app.to_dict() for app in self.applications.all()]
        return data


class JobPosition(db.Model):
    __tablename__ = 'job_positions'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.String(50), default='full-time')  # full-time, internship, contract
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    skills_required = db.Column(db.Text)  # comma-separated
    experience_required = db.Column(db.String(50))  # e.g., '0-1 years', '2-5 years'
    eligibility_branch = db.Column(db.String(200))  # comma-separated branches
    min_cgpa = db.Column(db.Float, default=0.0)
    eligibility_year = db.Column(db.Integer)
    benefits = db.Column(db.Text)
    location = db.Column(db.String(200))
    work_mode = db.Column(db.String(50), default='on-site')  # on-site, remote, hybrid
    openings = db.Column(db.Integer, default=1)
    application_deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, active, closed
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='job_position', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_company=False):
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'title': self.title,
            'description': self.description,
            'job_type': self.job_type,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'skills_required': self.skills_required,
            'experience_required': self.experience_required,
            'eligibility_branch': self.eligibility_branch,
            'min_cgpa': self.min_cgpa,
            'eligibility_year': self.eligibility_year,
            'benefits': self.benefits,
            'location': self.location,
            'work_mode': self.work_mode,
            'openings': self.openings,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'status': self.status,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_applications': self.applications.count() if self.applications else 0
        }
        if include_company and self.company:
            data['company'] = {
                'id': self.company.id,
                'name': self.company.name,
                'industry': self.company.industry,
                'location': self.company.location,
                'logo_url': self.company.logo_url
            }
        return data


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_positions.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='applied')
    # Status values: applied, shortlisted, interview, offer, selected, rejected
    feedback = db.Column(db.Text)
    interview_date = db.Column(db.Date)
    interview_time = db.Column(db.String(10))
    interview_link = db.Column(db.String(500))
    interview_location = db.Column(db.String(200))
    interview_notes = db.Column(db.Text)
    cover_letter = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: a student can apply only once per job
    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='unique_student_job_application'),
    )

    # Relationships
    placement = db.relationship('Placement', backref='application', uselist=False)

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'job_id': self.job_id,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'status': self.status,
            'feedback': self.feedback,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'interview_time': self.interview_time,
            'interview_link': self.interview_link,
            'interview_location': self.interview_location,
            'interview_notes': self.interview_notes,
            'cover_letter': self.cover_letter,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_details:
            if self.student:
                data['student'] = {
                    'id': self.student.id,
                    'name': self.student.name,
                    'roll_number': self.student.roll_number,
                    'branch': self.student.branch,
                    'cgpa': self.student.cgpa,
                    'year': self.student.year,
                    'skills': self.student.skills,
                    'email': self.student.user.email if self.student.user else None,
                    'phone': self.student.phone,
                    'resume_path': self.student.resume_path
                }
            if self.job_position:
                data['job'] = self.job_position.to_dict(include_company=True)
        return data


class Placement(db.Model):
    __tablename__ = 'placements'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_positions.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, unique=True)
    position = db.Column(db.String(200), nullable=False)
    salary = db.Column(db.Float)
    joining_date = db.Column(db.Date)
    offer_letter_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='confirmed')  # confirmed, joined, withdrawn
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'company_id': self.company_id,
            'job_id': self.job_id,
            'application_id': self.application_id,
            'position': self.position,
            'salary': self.salary,
            'joining_date': self.joining_date.isoformat() if self.joining_date else None,
            'offer_letter_path': self.offer_letter_path,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'student_name': self.student.name if self.student else None,
            'company_name': self.company.name if self.company else None,
            'job_title': self.job_position.title if self.job_position else None
        }

    # Relationship to JobPosition
    job_position = db.relationship('JobPosition', backref='placements')


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))  # info, success, warning, error
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'link': self.link,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
