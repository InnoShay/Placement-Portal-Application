"""Student routes - Profile, job browsing, applications, placements."""
import os
from datetime import datetime, date
from flask import Blueprint, request, jsonify, g, current_app, send_file
from werkzeug.utils import secure_filename
from models import db, Student, JobPosition, Application, Placement, Company, Notification
from utils.decorators import role_required
from utils.cache import cache

student_bp = Blueprint('student', __name__)


def get_current_student():
    """Get the student profile for the current user."""
    return Student.query.filter_by(user_id=g.current_user.id).first()


# ---- Student Profile ----

@student_bp.route('/api/student/profile', methods=['GET'])
@role_required('student')
def get_profile():
    """Get student profile."""
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    return jsonify({'student': student.to_dict(include_applications=True)}), 200


@student_bp.route('/api/student/profile', methods=['PUT'])
@role_required('student')
def update_profile():
    """Update student profile."""
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    data = request.get_json()

    updatable_fields = [
        'name', 'phone', 'branch', 'cgpa', 'year', 'skills',
        'bio', 'linkedin_url', 'github_url', 'experience', 'education', 'roll_number'
    ]

    for field in updatable_fields:
        if field in data:
            value = data[field]
            if field == 'cgpa':
                value = float(value) if value else None
            elif field == 'year':
                value = int(value) if value else None
            setattr(student, field, value)

    student.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Profile updated successfully', 'student': student.to_dict()}), 200


@student_bp.route('/api/student/profile/resume', methods=['POST'])
@role_required('student')
def upload_resume():
    """Upload or update resume."""
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    if 'resume' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    allowed_extensions = {'pdf', 'doc', 'docx'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return jsonify({'error': 'Only PDF, DOC, and DOCX files are allowed'}), 400

    # Create upload directory if it doesn't exist
    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    filename = secure_filename(f'resume_{student.id}_{student.roll_number or "file"}.{ext}')
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Remove old resume if exists
    if student.resume_path and os.path.exists(student.resume_path):
        try:
            os.remove(student.resume_path)
        except OSError:
            pass

    student.resume_path = filepath
    student.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Resume uploaded successfully',
        'resume_path': filepath
    }), 200


@student_bp.route('/api/student/resume/<int:student_id>', methods=['GET'])
@role_required('student', 'company', 'admin')
def download_resume(student_id):
    """Download a student's resume."""
    student = Student.query.get_or_404(student_id)
    if not student.resume_path or not os.path.exists(student.resume_path):
        return jsonify({'error': 'Resume not found'}), 404
    return send_file(student.resume_path, as_attachment=True)


# ---- Job Browsing ----

@student_bp.route('/api/student/jobs', methods=['GET'])
@role_required('student')
def browse_jobs():
    """Browse approved and active job postings."""
    student = get_current_student()
    search = request.args.get('search', '').strip()
    branch = request.args.get('branch', '').strip()
    job_type = request.args.get('job_type', '').strip()
    company_name = request.args.get('company', '').strip()
    min_salary = request.args.get('min_salary', type=float)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    eligible_only = request.args.get('eligible_only', '').strip().lower() == 'true'

    query = JobPosition.query.filter_by(status='approved', is_active=True)

    # Only show jobs from approved, non-blacklisted companies
    query = query.join(Company).filter(
        Company.approval_status == 'approved',
        Company.is_blacklisted == False
    )

    if search:
        query = query.filter(
            db.or_(
                JobPosition.title.ilike(f'%{search}%'),
                JobPosition.skills_required.ilike(f'%{search}%'),
                JobPosition.description.ilike(f'%{search}%'),
                Company.name.ilike(f'%{search}%')
            )
        )

    if branch:
        query = query.filter(
            db.or_(
                JobPosition.eligibility_branch.ilike(f'%{branch}%'),
                JobPosition.eligibility_branch == '',
                JobPosition.eligibility_branch.is_(None)
            )
        )

    if job_type:
        query = query.filter_by(job_type=job_type)

    if company_name:
        query = query.filter(Company.name.ilike(f'%{company_name}%'))

    if min_salary:
        query = query.filter(JobPosition.salary_max >= min_salary)

    # Filter for eligible jobs only
    if eligible_only and student:
        if student.cgpa:
            query = query.filter(
                db.or_(
                    JobPosition.min_cgpa <= student.cgpa,
                    JobPosition.min_cgpa.is_(None)
                )
            )
        if student.branch:
            query = query.filter(
                db.or_(
                    JobPosition.eligibility_branch.ilike(f'%{student.branch}%'),
                    JobPosition.eligibility_branch == '',
                    JobPosition.eligibility_branch.is_(None)
                )
            )

    # Only show jobs with future or today's deadline
    query = query.filter(JobPosition.application_deadline >= date.today())

    pagination = query.order_by(JobPosition.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Check which jobs the student has already applied for
    applied_job_ids = set()
    if student:
        applied_apps = Application.query.filter_by(student_id=student.id).all()
        applied_job_ids = {a.job_id for a in applied_apps}

    jobs_data = []
    for job in pagination.items:
        job_dict = job.to_dict(include_company=True)
        job_dict['has_applied'] = job.id in applied_job_ids
        # Check eligibility
        eligible = True
        if student:
            if job.min_cgpa and student.cgpa and student.cgpa < job.min_cgpa:
                eligible = False
            if job.eligibility_branch and student.branch:
                allowed_branches = [b.strip().lower() for b in job.eligibility_branch.split(',')]
                if student.branch.lower() not in allowed_branches and allowed_branches != ['']:
                    eligible = False
        job_dict['is_eligible'] = eligible
        jobs_data.append(job_dict)

    return jsonify({
        'jobs': jobs_data,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@student_bp.route('/api/student/jobs/<int:job_id>', methods=['GET'])
@role_required('student')
def get_job_detail(job_id):
    """Get detailed job posting info."""
    job = JobPosition.query.get_or_404(job_id)
    student = get_current_student()

    job_dict = job.to_dict(include_company=True)

    # Check if already applied
    if student:
        existing = Application.query.filter_by(
            student_id=student.id, job_id=job_id
        ).first()
        job_dict['has_applied'] = existing is not None
        job_dict['application'] = existing.to_dict() if existing else None

    return jsonify({'job': job_dict}), 200


# ---- Job Applications ----

@student_bp.route('/api/student/jobs/<int:job_id>/apply', methods=['POST'])
@role_required('student')
def apply_for_job(job_id):
    """Apply for a job posting."""
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    if student.is_blacklisted:
        return jsonify({'error': 'Your account has been blacklisted'}), 403

    job = JobPosition.query.get_or_404(job_id)

    # Validations
    if job.status != 'approved' or not job.is_active:
        return jsonify({'error': 'This placement drive is not currently accepting applications'}), 400

    if job.application_deadline < date.today():
        return jsonify({'error': 'The application deadline has passed'}), 400

    # Check for duplicate application
    existing = Application.query.filter_by(
        student_id=student.id, job_id=job_id
    ).first()
    if existing:
        return jsonify({'error': 'You have already applied for this position'}), 409

    # Eligibility check
    if job.min_cgpa and student.cgpa and student.cgpa < job.min_cgpa:
        return jsonify({'error': f'Minimum CGPA requirement is {job.min_cgpa}. Your CGPA: {student.cgpa}'}), 400

    if job.eligibility_branch and student.branch:
        allowed_branches = [b.strip().lower() for b in job.eligibility_branch.split(',')]
        if allowed_branches != [''] and student.branch.lower() not in allowed_branches:
            return jsonify({
                'error': f'This position is only for {job.eligibility_branch} branches'
            }), 400

    data = request.get_json() or {}

    application = Application(
        student_id=student.id,
        job_id=job_id,
        status='applied',
        cover_letter=data.get('cover_letter', '')
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({
        'message': f'Successfully applied for {job.title}',
        'application': application.to_dict(include_details=True)
    }), 201


@student_bp.route('/api/student/applications', methods=['GET'])
@role_required('student')
def get_applications():
    """Get all applications by the student."""
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    status = request.args.get('status', '').strip()
    query = Application.query.filter_by(student_id=student.id)

    if status:
        query = query.filter_by(status=status)

    applications = query.order_by(Application.application_date.desc()).all()

    return jsonify({
        'applications': [a.to_dict(include_details=True) for a in applications],
        'total': len(applications)
    }), 200


@student_bp.route('/api/student/applications/<int:app_id>', methods=['GET'])
@role_required('student')
def get_application_detail(app_id):
    """Get detailed application info."""
    student = get_current_student()
    application = Application.query.filter_by(
        id=app_id, student_id=student.id
    ).first()

    if not application:
        return jsonify({'error': 'Application not found'}), 404

    return jsonify({'application': application.to_dict(include_details=True)}), 200


# ---- Placements ----

@student_bp.route('/api/student/placements', methods=['GET'])
@role_required('student')
def get_placements():
    """Get placement history."""
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    placements = Placement.query.filter_by(student_id=student.id).order_by(
        Placement.created_at.desc()
    ).all()

    return jsonify({
        'placements': [p.to_dict() for p in placements],
        'total': len(placements)
    }), 200


@student_bp.route('/api/student/offer-letter/<int:placement_id>', methods=['GET'])
@role_required('student')
def download_offer_letter(placement_id):
    """Download offer letter for a placement."""
    student = get_current_student()
    placement = Placement.query.filter_by(
        id=placement_id, student_id=student.id
    ).first()

    if not placement:
        return jsonify({'error': 'Placement not found'}), 404

    if not placement.offer_letter_path or not os.path.exists(placement.offer_letter_path):
        return jsonify({'error': 'Offer letter not available'}), 404

    return send_file(placement.offer_letter_path, as_attachment=True)


# ---- Notifications ----

@student_bp.route('/api/student/notifications', methods=['GET'])
@role_required('student')
def get_notifications():
    """Get student notifications."""
    notifications = Notification.query.filter_by(
        user_id=g.current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()

    return jsonify({
        'notifications': [n.to_dict() for n in notifications],
        'unread_count': sum(1 for n in notifications if not n.is_read)
    }), 200


@student_bp.route('/api/student/notifications/<int:notif_id>/read', methods=['PUT'])
@role_required('student')
def mark_notification_read(notif_id):
    """Mark a notification as read."""
    notification = Notification.query.filter_by(
        id=notif_id, user_id=g.current_user.id
    ).first()

    if notification:
        notification.is_read = True
        db.session.commit()

    return jsonify({'message': 'Notification marked as read'}), 200


@student_bp.route('/api/student/dashboard', methods=['GET'])
@role_required('student')
def student_dashboard():
    """Get student dashboard data."""
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    total_applications = student.applications.count()
    applied = student.applications.filter_by(status='applied').count()
    shortlisted = student.applications.filter_by(status='shortlisted').count()
    interview = student.applications.filter_by(status='interview').count()
    selected = student.applications.filter_by(status='selected').count()
    rejected = student.applications.filter_by(status='rejected').count()

    # Upcoming interviews
    upcoming_interviews = Application.query.filter(
        Application.student_id == student.id,
        Application.status == 'interview',
        Application.interview_date >= date.today()
    ).order_by(Application.interview_date.asc()).all()

    # Available drives count
    available_drives = JobPosition.query.filter_by(
        status='approved', is_active=True
    ).filter(
        JobPosition.application_deadline >= date.today()
    ).count()

    return jsonify({
        'student': student.to_dict(),
        'stats': {
            'total_applications': total_applications,
            'applied': applied,
            'shortlisted': shortlisted,
            'interview': interview,
            'selected': selected,
            'rejected': rejected,
            'available_drives': available_drives,
            'is_placed': student.is_placed
        },
        'upcoming_interviews': [a.to_dict(include_details=True) for a in upcoming_interviews]
    }), 200
